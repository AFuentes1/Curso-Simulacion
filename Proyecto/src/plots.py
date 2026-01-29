# src/plots.py
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Dict, List, Any, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.config import make_base_config, ModelConfig, ALL_STATIONS, CAJA, DistSpec
from src.simulation import run_replications


PCTS = [5, 10, 25, 50, 75, 90, 95]


# -----------------------------
# Helpers básicos
# -----------------------------
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_dirs() -> Tuple[Path, Path]:
    out_dir = project_root() / "outputs"
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    return out_dir, fig_dir


def mode_rounded_int(x: np.ndarray) -> int:
    xr = np.rint(x).astype(int)
    if xr.size == 0:
        return 0
    xr = xr[xr >= 0]
    if xr.size == 0:
        return 0
    counts = np.bincount(xr)
    return int(np.argmax(counts))


def stats_summary(x: np.ndarray) -> Dict[str, Any]:
    x = np.asarray(x, dtype=float)
    q1, q2, q3 = np.percentile(x, [25, 50, 75])
    pct_vals = {f"p{p}": float(np.percentile(x, p)) for p in PCTS}
    return {
        "n": int(len(x)),
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "var": float(np.var(x, ddof=1)) if len(x) > 1 else 0.0,
        "mode_int": mode_rounded_int(x),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
        "q1": float(q1),
        "q2": float(q2),
        "q3": float(q3),
        **pct_vals,
    }


def format_stats_box(s: Dict[str, Any]) -> str:
    # texto corto para poner dentro del gráfico
    return (
        f"n={s['n']}\n"
        f"media={s['mean']:.3f}\n"
        f"mediana={s['median']:.3f}\n"
        f"var={s['var']:.3f}\n"
        f"moda(int)={s['mode_int']}\n"
        f"min={s['min']:.3f}  max={s['max']:.3f}\n"
        f"Q1={s['q1']:.3f}  Q2={s['q2']:.3f}  Q3={s['q3']:.3f}\n"
        f"P10={s['p10']:.3f}  P90={s['p90']:.3f}"
    )


# -----------------------------
# Variantes de configuración (e) y (d)
# -----------------------------
def with_pollo_50(cfg: ModelConfig) -> ModelConfig:
    # Ajuste simple: pollo total = 0.50
    #  solo_refresco=0.30, frito_y_refresco=0.20, pollo_y_refresco=0.40, combo=0.10
    ot = {o.name: o for o in cfg.order_types}
    new_order_types = [
        replace(ot["solo_refresco"], prob=0.30),
        replace(ot["frito_y_refresco"], prob=0.20),
        replace(ot["pollo_y_refresco"], prob=0.40),
        replace(ot["combo_completo"], prob=0.10),
    ]
    return replace(cfg, order_types=new_order_types)


def with_cashier_mean(cfg: ModelConfig, mean_min: float) -> ModelConfig:
    new_services = dict(cfg.service_dists)
    new_services[CAJA] = DistSpec(name="expon", shape=(), loc=0.0, scale=float(mean_min), units="min")
    return replace(cfg, service_dists=new_services)


# -----------------------------
# Cargar soluciones (top 3) desde outputs
# -----------------------------
def load_solutions(out_dir: Path) -> List[Dict[str, Any]]:
    files = [
        ("a", out_dir / "search_a_min_cost.csv", "base"),
        ("b", out_dir / "search_b_budget_2000.csv", "base"),
        ("c", out_dir / "search_c_budget_3000.csv", "base"),
        ("e", out_dir / "search_e_pollo_50.csv", "pollo50"),
    ]

    sols: List[Dict[str, Any]] = []
    for tag, f, variant in files:
        if not f.exists():
            continue
        df = pd.read_csv(f)
        # quitar duplicados por servidores (por el caso (a) que sale repetido)
        df = df.drop_duplicates(subset=["caja", "freidora", "refrescos", "pollo"])
        for rank, row in enumerate(df.itertuples(index=False), 1):
            servers = {
                "caja": int(getattr(row, "caja")),
                "freidora": int(getattr(row, "freidora")),
                "refrescos": int(getattr(row, "refrescos")),
                "pollo": int(getattr(row, "pollo")),
            }
            sols.append({
                "tag": tag,
                "rank": rank,
                "variant": variant,
                "servers": servers,
                "cost": float(getattr(row, "cost")),
            })

    # agregar (d) como “solución extra” (no viene en csv)
    sols.append({
        "tag": "d",
        "rank": 1,
        "variant": "cashier2",
        "servers": {"caja": 4, "freidora": 6, "refrescos": 5, "pollo": 5},
        "cost": np.nan,
    })

    return sols


# -----------------------------
# Correr réplica y armar “muestra”
# -----------------------------
def run_solution(cfg: ModelConfig, servers: Dict[str, int]) -> Dict[str, Any]:
    results = run_replications(cfg, servers)

    # muestra: 1 valor por réplica
    wq_total = np.array([r.mean_queue_wait_total for r in results], dtype=float)

    # por estación: 1 valor por réplica
    per_station = {}
    for st in ALL_STATIONS:
        per_station[st] = np.array([float(r.per_station[st]["avg_queue_wait"]) for r in results], dtype=float)

    return {"wq_total": wq_total, "per_station": per_station, "nrep": len(results)}


# -----------------------------
# Gráficas
# -----------------------------
def plot_hist_abs(x: np.ndarray, title: str, fig_path: Path) -> None:
    s = stats_summary(x)
    mean, med = s["mean"], s["median"]
    q1, q3 = s["q1"], s["q3"]

    plt.figure()
    plt.hist(x, bins=15)
    plt.axvline(mean, linestyle="--", linewidth=2, label=f"Media={mean:.3f}")
    plt.axvline(med, linestyle=":", linewidth=2, label=f"Mediana={med:.3f}")
    plt.axvline(q1, linestyle="-.", linewidth=1.5, label=f"Q1={q1:.3f}")
    plt.axvline(q3, linestyle="-.", linewidth=1.5, label=f"Q3={q3:.3f}")
    plt.title(title + " (Frecuencia absoluta)")
    plt.xlabel("Espera total en colas (min) por réplica")
    plt.ylabel("Frecuencia (conteo)")
    plt.legend()
    plt.gca().text(
        0.98, 0.98, format_stats_box(s),
        transform=plt.gca().transAxes,
        ha="right", va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
    )
    plt.tight_layout()
    plt.savefig(fig_path, dpi=200)
    plt.close()


def plot_hist_rel(x: np.ndarray, title: str, fig_path: Path) -> None:
    s = stats_summary(x)
    mean, med = s["mean"], s["median"]
    q1, q3 = s["q1"], s["q3"]

    plt.figure()
    weights = np.ones_like(x) / len(x)
    plt.hist(x, bins=15, weights=weights)
    plt.axvline(mean, linestyle="--", linewidth=2, label=f"Media={mean:.3f}")
    plt.axvline(med, linestyle=":", linewidth=2, label=f"Mediana={med:.3f}")
    plt.axvline(q1, linestyle="-.", linewidth=1.5, label=f"Q1={q1:.3f}")
    plt.axvline(q3, linestyle="-.", linewidth=1.5, label=f"Q3={q3:.3f}")
    plt.title(title + " (Frecuencia relativa)")
    plt.xlabel("Espera total en colas (min) por réplica")
    plt.ylabel("Frecuencia relativa")
    plt.legend()
    plt.gca().text(
        0.98, 0.98, format_stats_box(s),
        transform=plt.gca().transAxes,
        ha="right", va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
    )
    plt.tight_layout()
    plt.savefig(fig_path, dpi=200)
    plt.close()


def plot_boxplot(x: np.ndarray, title: str, fig_path: Path) -> None:
    plt.figure()
    plt.boxplot(x, vert=True)
    plt.title(title + " (Boxplot / cuartiles)")
    plt.ylabel("Espera total en colas (min) por réplica")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=200)
    plt.close()


def plot_covariance(per_station: Dict[str, np.ndarray], title: str, fig_path: Path) -> Dict[str, float]:
    stations = list(per_station.keys())
    X = np.column_stack([per_station[st] for st in stations])
    cov = np.cov(X, rowvar=False, ddof=1) if X.shape[0] > 1 else np.zeros((len(stations), len(stations)))

    plt.figure()
    plt.imshow(cov)
    plt.colorbar()
    plt.xticks(range(len(stations)), stations, rotation=45, ha="right")
    plt.yticks(range(len(stations)), stations)
    plt.title(title + " (Covarianza por estación)")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=200)
    plt.close()

    # devolver covarianzas para CSV
    out: Dict[str, float] = {}
    for i, a in enumerate(stations):
        for j, b in enumerate(stations):
            out[f"cov_{a}_{b}"] = float(cov[i, j])
    return out


# -----------------------------
# (i) Sensibilidad (EXTRA): variar prob de "pollo" y ver espera
# -----------------------------
def sensitivity_pollo(cfg: ModelConfig, servers: Dict[str, int], fig_path: Path) -> None:
    # Variamos pollo_y_refresco de 0.25 hasta 0.55 (pasos), ajustando frito para que sume 1.
    # (solo_refresco=0.30, combo=0.10 se quedan fijos)
    base = {o.name: o for o in cfg.order_types}

    ps = np.linspace(0.25, 0.55, 7)  # 7 puntos
    waits = []

    for p_polloyr in ps:
        p_solo = 0.30
        p_combo = 0.10
        p_frito = 1.0 - (p_solo + p_combo + p_polloyr)
        if p_frito <= 0:
            waits.append(np.nan)
            continue

        cfg_var = replace(cfg, order_types=[
            replace(base["solo_refresco"], prob=p_solo),
            replace(base["frito_y_refresco"], prob=float(p_frito)),
            replace(base["pollo_y_refresco"], prob=float(p_polloyr)),
            replace(base["combo_completo"], prob=p_combo),
        ])

        # para que sea rápido (EXTRA): menos reps/clientes
        cfg_fast = replace(cfg_var, settings=replace(cfg_var.settings, n_customers=800, warmup_customers=100, replications=5))
        res = run_replications(cfg_fast, servers)
        w = float(np.mean([r.mean_queue_wait_total for r in res]))
        waits.append(w)

    plt.figure()
    plt.plot(ps, waits, marker="o")
    plt.title("Sensibilidad: espera vs P(pollo_y_refresco)")
    plt.xlabel("P(pollo_y_refresco)")
    plt.ylabel("Espera total en colas (min)")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=200)
    plt.close()


# -----------------------------
# Main: genera todo
# -----------------------------
def main():
    out_dir, fig_dir = ensure_dirs()
    cfg_base = make_base_config()

    sols = load_solutions(out_dir)
    all_rows = []

    for sol in sols:
        tag = sol["tag"]
        rank = sol["rank"]
        variant = sol["variant"]
        servers = sol["servers"]

        # armar config según caso
        cfg = cfg_base
        if variant == "pollo50":
            cfg = with_pollo_50(cfg_base)
        elif variant == "cashier2":
            cfg = with_cashier_mean(cfg_base, mean_min=2.0)

        # correr y armar muestra
        data = run_solution(cfg, servers)
        wq = data["wq_total"]
        per_station = data["per_station"]

        # stats de la muestra principal (espera total)
        s = stats_summary(wq)

        # covarianza por estación
        covs = {} if per_station is None else plot_covariance(
            per_station,
            title=f"{tag.upper()}#{rank} - servers={servers}",
            fig_path=fig_dir / f"{tag}_{rank}_cov.png"
        )

        # plots de frecuencias (abs/rel) + box
        plot_hist_abs(
            wq,
            title=f"{tag.upper()}#{rank} - servers={servers}",
            fig_path=fig_dir / f"{tag}_{rank}_hist_abs.png"
        )
        plot_hist_rel(
            wq,
            title=f"{tag.upper()}#{rank} - servers={servers}",
            fig_path=fig_dir / f"{tag}_{rank}_hist_rel.png"
        )
        plot_boxplot(
            wq,
            title=f"{tag.upper()}#{rank} - servers={servers}",
            fig_path=fig_dir / f"{tag}_{rank}_box.png"
        )

        # sensibilidad (EXTRA) solo para soluciones que sí valen la pena (a y e y d)
        if tag in {"a", "e", "d"}:
            sensitivity_pollo(cfg_base, servers, fig_dir / f"{tag}_{rank}_sens_pollo.png")

        # fila para CSV
        row = {
            "tag": tag,
            "rank": rank,
            "variant": variant,
            "servers": str(servers),
            "cost": sol.get("cost", np.nan),
            **s,
            **covs,
        }
        all_rows.append(row)

    df = pd.DataFrame(all_rows)
    df.to_csv(out_dir / "stats_point3_all.csv", index=False, encoding="utf-8-sig")

    print("\n✅ Listo. Guardé:")
    print(" - outputs/stats_point3_all.csv")
    print(" - outputs/figures/* (hist_abs, hist_rel, box, cov, sens_*)")


if __name__ == "__main__":
    main()