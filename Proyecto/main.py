# main.py
from src.config import make_base_config
from src.simulation import run_replications

def main():
    cfg = make_base_config()

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

    servers = {"caja": 4, "freidora": 2, "refrescos": 2, "pollo": 2}
    results = run_replications(cfg, servers)
    print("Tiempo en sistema:", results[0].mean_time_in_system)
    print("Espera total en colas:", results[0].mean_queue_wait_total)


    

if __name__ == "__main__":
    main()
