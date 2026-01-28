# main.py
from src.config import make_base_config, DistSpec
import src.config
from src.simulation import run_replications
from itertools import product
                                                                                  
def cost_of(servers, costs):
    return sum(servers[k] * costs[k] for k in servers)

def solve_2c(cfg):
    best = None

    # rangos razonables (no tiene sentido probar 20 cajas)
    for caja, fre, ref, pol in product(
        range(1, 8),   # caja
        range(1, 3),  # freidora
        range(1, 2),   # refrescos
        range(1, 15)   # pollo
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

def compare_cashier(cfg, servers):
    # Escenario base
    results_base = src.simulation.run_replications(cfg, servers)
    wait_base = sum(r.mean_queue_wait_total for r in results_base) / len(results_base)

    # Nuevo config con caja = 2 min
    new_services = dict(cfg.service_dists)
    new_services[src.config.CAJA] = src.config.DistSpec(
        name="expon",
        scale=2.0,
        units="min"
    )

    cfg_fast = src.config.ModelConfig(
        arrival_dist=cfg.arrival_dist,
        service_dists=new_services,
        order_types=cfg.order_types,
        costs=cfg.costs,
        settings=cfg.settings,
        wait_threshold_minutes=cfg.wait_threshold_minutes
    )

    results_fast = src.simulation.run_replications(cfg_fast, servers)
    wait_fast = sum(r.mean_queue_wait_total for r in results_fast) / len(results_fast)

    return {
        "wait_base": wait_base,
        "wait_fast": wait_fast,
        "delta_wait": wait_base - wait_fast
    }


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

    cmp = compare_cashier(cfg, servers)

    print("\n=== 2(d) ===")
    print("Espera base:", cmp["wait_base"])
    print("Espera con caja = 2 min:", cmp["wait_fast"])
    print("Reducción:", cmp["delta_wait"])




    

if __name__ == "__main__":
    main()
