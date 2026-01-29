# src/search.py
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Dict, List, Any
import itertools

import pandas as pd

from src.config import make_base_config, ModelConfig, ALL_STATIONS, DistSpec, CAJA
from src.simulation import run_replications
from src.metrics import summarize_replications


def config_cost(cfg: ModelConfig, servers: Dict[str, int]) -> float:
    return sum(cfg.costs.cost_per_server[st] * servers[st] for st in ALL_STATIONS)


def _with_search_settings(cfg: ModelConfig, n_customers: int, warmup_customers: int, replications: int) -> ModelConfig:
    new_settings = replace(cfg.settings, n_customers=n_customers, warmup_customers=warmup_customers, replications=replications)
    return replace(cfg, settings=new_settings)


def evaluate(cfg: ModelConfig, servers: Dict[str, int]) -> Dict[str, Any]:
    """Corre simulación (reps) y devuelve métricas resumidas."""
    results = run_replications(cfg, servers)
    summ = summarize_replications(results)

    return {
        "servers": servers,
        "cost": config_cost(cfg, servers),
        "wait_mean": summ["queue_wait_total"]["mean"],         # espera total en colas
        "wait_ci_low": summ["queue_wait_total"]["low"],
        "wait_ci_high": summ["queue_wait_total"]["high"],
        "tis_mean": summ["time_in_system"]["mean"],            # tiempo en sistema
    }


def generate_combos(max_each: int) -> List[Dict[str, int]]:
    """Genera combinaciones 1..max_each para cada estación."""
    combos = []
    for caja, freidora, refrescos, pollo in itertools.product(range(1, max_each + 1), repeat=4):
        combos.append({"caja": caja, "freidora": freidora, "refrescos": refrescos, "pollo": pollo})
    return combos


def top3_min_cost_meeting_wait(cfg_full: ModelConfig, wait_threshold: float = 3.0) -> List[Dict[str, Any]]:
    """
    (a) Top 3 por MENOR COSTO, cumpliendo espera_total <= 3.
    Se hace búsqueda rápida con menos reps/clientes y luego reevaluación full.
    """
    # búsqueda rápida
    cfg_fast = _with_search_settings(cfg_full, n_customers=600, warmup_customers=100, replications=2)
    found: List[Dict[str, Any]] = []
    max_each = 4

    while max_each <= 6 and len(found) < 3:
        combos = generate_combos(max_each)

        # ordenar por costo ascendente para encontrar el mínimo más rápido
        combos.sort(key=lambda s: config_cost(cfg_fast, s))

        for servers in combos:
            if len(found) >= 3:
                break

            ev = evaluate(cfg_fast, servers)
            if ev["wait_mean"] <= wait_threshold:
                found.append(ev)

        max_each += 1

    if not found:
        return []

    # reevaluar "full" y seleccionar top 3 por costo (cumpliendo)
    reevaluated = []
    for item in found:
        ev_full = evaluate(cfg_full, item["servers"])
        if ev_full["wait_mean"] <= wait_threshold:
            reevaluated.append(ev_full)

    reevaluated.sort(key=lambda x: x["cost"])
    return reevaluated[:3]


def top3_best_under_budget(cfg_full: ModelConfig, budget: float) -> List[Dict[str, Any]]:
    """
    (b) Top 3 "mejores" bajo presupuesto: minimiza espera_total; desempate por menor costo.
    """
    cfg_fast = _with_search_settings(cfg_full, n_customers=1200, warmup_customers=200, replications=6)

    max_each = 12
    combos = generate_combos(max_each)

    combos = [s for s in combos if config_cost(cfg_fast, s) <= budget]

    scored: List[Dict[str, Any]] = []
    for servers in combos:
        ev = evaluate(cfg_fast, servers)
        scored.append(ev)

    scored.sort(key=lambda x: (x["wait_mean"], x["cost"]))
    shortlist = scored[:10]

    reevaluated = [evaluate(cfg_full, x["servers"]) for x in shortlist]
    reevaluated.sort(key=lambda x: (x["wait_mean"], x["cost"]))
    return reevaluated[:3]


def save_results(tag: str, rows: List[Dict[str, Any]]) -> None:
    project_root = Path(__file__).resolve().parents[1]
    out_dir = project_root / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    flat_rows = []
    for r in rows:
        s = r["servers"]
        flat_rows.append({
            "tag": tag,
            "cost": r["cost"],
            "wait_mean": r["wait_mean"],
            "wait_ci_low": r["wait_ci_low"],
            "wait_ci_high": r["wait_ci_high"],
            "tis_mean": r["tis_mean"],
            "caja": s["caja"],
            "freidora": s["freidora"],
            "refrescos": s["refrescos"],
            "pollo": s["pollo"],
        })

    df = pd.DataFrame(flat_rows)
    df.to_csv(out_dir / f"search_{tag}.csv", index=False, encoding="utf-8-sig")


def with_pollo_50(cfg: ModelConfig) -> ModelConfig:
    ot = {o.name: o for o in cfg.order_types}

    new_order_types = [
        replace(ot["solo_refresco"], prob=0.30),
        replace(ot["frito_y_refresco"], prob=0.20),
        replace(ot["pollo_y_refresco"], prob=0.40),
        replace(ot["combo_completo"], prob=0.10),
    ]

    return replace(cfg, order_types=new_order_types)


# -------------------------
# (d) movido aquí: comparar caja base vs caja media=2min
# -------------------------
def compare_cashier(cfg: ModelConfig, servers: Dict[str, int], cashier_mean_min: float = 2.0) -> Dict[str, float]:
    # Escenario base
    results_base = run_replications(cfg, servers)
    summ_base = summarize_replications(results_base)
    wait_base = summ_base["queue_wait_total"]["mean"]

    # Nuevo config con caja = cashier_mean_min
    new_services = dict(cfg.service_dists)
    new_services[CAJA] = DistSpec(
        name="expon",
        scale=float(cashier_mean_min),
        units="min"
    )
    cfg_fast = replace(cfg, service_dists=new_services)

    results_fast = run_replications(cfg_fast, servers)
    summ_fast = summarize_replications(results_fast)
    wait_fast = summ_fast["queue_wait_total"]["mean"]

    return {
        "wait_base": wait_base,
        "wait_fast": wait_fast,
        "delta_wait": wait_base - wait_fast
    }


def main():
    cfg = make_base_config()

    # -------------------------
    # (a) costo mínimo cumpliendo <= 3
    # -------------------------
    print("\n=== (a) Costo mínimo para garantizar espera promedio ≤ 3 min (Top 3) ===")
    top_a = top3_min_cost_meeting_wait(cfg, wait_threshold=cfg.wait_threshold_minutes)

    if not top_a:
        print("No se encontró configuración que cumpla dentro de los límites de búsqueda.")
    else:
        for i, r in enumerate(top_a, 1):
            print(f"{i}) cost=${r['cost']:.0f}  wait={r['wait_mean']:.3f}  servers={r['servers']}")
        save_results("a_min_cost", top_a)

    # -------------------------
    # (b) mejor bajo $2000
    # -------------------------
    print("\n=== (b) Mejor configuración con presupuesto $2000 (Top 3) ===")
    top_b = top3_best_under_budget(cfg, budget=2000.0)

    if top_b and min(r["wait_mean"] for r in top_b) > cfg.wait_threshold_minutes:
        print(f"\nNOTA: Con presupuesto $2000 NO se logra espera ≤ {cfg.wait_threshold_minutes} min.")
        print("Se reportan las configuraciones que MINIMIZAN la espera dentro del presupuesto.\n")

    for i, r in enumerate(top_b, 1):
        print(f"{i}) cost=${r['cost']:.0f}  wait={r['wait_mean']:.3f}  servers={r['servers']}")
    save_results("b_budget_2000", top_b)

    # -------------------------
    # (c) mejor bajo $3000
    # -------------------------
    print("\n=== (c) Mejor configuración con presupuesto $3000 (Top 3) ===")
    top_c = top3_best_under_budget(cfg, budget=3000.0)

    if top_c and min(r["wait_mean"] for r in top_c) > cfg.wait_threshold_minutes:
        print(f"\nNOTA: Con presupuesto $3000 NO se logra espera ≤ {cfg.wait_threshold_minutes} min.")
        print("Se reportan las configuraciones que MINIMIZAN la espera dentro del presupuesto.\n")

    for i, r in enumerate(top_c, 1):
        print(f"{i}) cost=${r['cost']:.0f}  wait={r['wait_mean']:.3f}  servers={r['servers']}")
    save_results("c_budget_3000", top_c)

    # -------------------------
    # (d) caja con media 2 min (MISMA dotación base)
    # -------------------------
    servers_d = {"caja": 4, "freidora": 6, "refrescos": 5, "pollo": 5}
    cmp = compare_cashier(cfg, servers_d, cashier_mean_min=2.0)

    print("\n=== (d) Caja con media = 2 min (misma dotación de servidores) ===")
    print("Servidores:", servers_d)
    print("Espera base:", cmp["wait_base"])
    print("Espera con caja = 2 min:", cmp["wait_fast"])
    print("Reducción:", cmp["delta_wait"])

    # -------------------------
    # (e) P(pollo)=50% manteniendo <= 3
    # -------------------------
    print("\n=== (e) Ajuste si P(pollo)=50% manteniendo espera promedio ≤ 3 min (Top 3) ===")
    cfg_e = with_pollo_50(cfg)

    top_e = top3_min_cost_meeting_wait(cfg_e, wait_threshold=cfg_e.wait_threshold_minutes)

    if not top_e:
        print("No se encontró configuración que cumpla dentro de los límites de búsqueda.")
    else:
        for i, r in enumerate(top_e, 1):
            print(f"{i}) cost=${r['cost']:.0f}  wait={r['wait_mean']:.3f}  servers={r['servers']}")
        save_results("e_pollo_50", top_e)


if __name__ == "__main__":
    main()