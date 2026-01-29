# main.py
from src.config import make_base_config
import src.config
from src.simulation import run_replications
from itertools import product
import src.simulation


def cost_of(servers, costs):
    return sum(servers[k] * costs[k] for k in servers)


def solve_2c(cfg):
    best = None

    # rangos razonables (no tiene sentido probar 20 cajas)
    for caja, fre, ref, pol in product(
        range(1, 8),  # caja
        range(1, 8),  # freidora (antes 1..2)
        range(1, 8),  # refrescos (antes SIEMPRE 1)
        range(1, 15)  # pollo
    ):
        servers = {
            "caja": caja,
            "freidora": fre,
            "refrescos": ref,
            "pollo": pol
        }

        cost = cost_of(servers, cfg.costs.cost_per_server)
        if cost > 3000:
            continue

        results = run_replications(cfg, servers)
        mean_wait = sum(r.mean_queue_wait_total for r in results) / len(results)

        if best is None or mean_wait < best["wait"]:
            best = {
                "servers": servers,
                "cost": cost,
                "wait": mean_wait
            }
    return best


def main():
    cfg = make_base_config()

    print(cfg.costs.cost_per_server)

    print("✅ Proyecto listo. Configuración base cargada.\n")
    print("Distribución de llegadas:", cfg.arrival_dist)
    print("\nDistribuciones de servicio:")
    for k, v in cfg.service_dists.items():
        print(f" - {k}: {v}")

    print("\nTipos de pedido:")
    for o in cfg.order_types:
        print(f" - {o.name}: prob={o.prob}, estaciones={o.stations}")

    print("\nCostos por servidor:")
    for k, v in cfg.costs.cost_per_server.items():
        print(f" - {k}: ${v}")

    print("\nSettings:", cfg.settings)
    print("\nObjetivo: espera promedio ≤", cfg.wait_threshold_minutes, "min")

    servers = {"caja": 4, "freidora": 6, "refrescos": 5, "pollo": 5}

    """
    results = run_replications(cfg, servers)
    print("Tiempo en sistema:", results[0].mean_time_in_system)
    print("POR ESTACIÓN:", results[0].per_station)
    print("Espera total en colas:", results[0].mean_queue_wait_total)
    """

    """
    best_2c = solve_2c(cfg)
    print("\n=== RESULTADO 2(c) ===")
    print("Servidores:", best_2c["servers"])
    print("Costo total:", best_2c["cost"])
    print("Espera promedio:", best_2c["wait"])
    """


if __name__ == "__main__":
    main()