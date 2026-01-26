# src/simulation.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import numpy as np
from scipy import stats

from src.config import ModelConfig, DistSpec, CAJA, ALL_STATIONS
 

# -----------------------------
# Helpers: distribución -> scipy rv
# -----------------------------
def _get_rv(spec: DistSpec):
    if not hasattr(stats, spec.name):
        raise ValueError(f"Distribución '{spec.name}' no existe en scipy.stats.")
    dist = getattr(stats, spec.name)
    return dist(*spec.shape, loc=spec.loc, scale=spec.scale)


# -----------------------------
# Estación multi-servidor FCFS
# -----------------------------
@dataclass
class StationMetrics:
    n_jobs: int = 0
    total_wait: float = 0.0       # espera en cola (sin servicio)
    total_service: float = 0.0    # tiempo de servicio
    last_completion: float = 0.0  # último fin de servicio


class Station:
    """
    Cola FCFS con c servidores.
    Para cada llegada t y servicio s:
      start = max(t, min(server_available))
      finish = start + s
    """
    def __init__(self, servers: int):
        if servers < 1:
            raise ValueError("servers debe ser >= 1")
        self.servers = servers
        self.avail = np.zeros(servers, dtype=float)  # disponibilidad de cada servidor
        self.m = StationMetrics()

    def process(self, arrival_time: float, service_time: float) -> Tuple[float, float]:
        i = int(np.argmin(self.avail))
        start = max(arrival_time, self.avail[i])
        wait = start - arrival_time
        finish = start + service_time

        self.avail[i] = finish

        self.m.n_jobs += 1
        self.m.total_wait += wait
        self.m.total_service += service_time
        if finish > self.m.last_completion:
            self.m.last_completion = finish

        return finish, wait


# -----------------------------
# Resultado de una réplica
# -----------------------------
@dataclass
class ReplicationResult:
    mean_time_in_system: float
    mean_queue_wait_total: float
    mean_queue_wait_cashier: float
    per_station: Dict[str, Dict[str, float]]
    n_effective: int  # clientes usados (después de warmup)


# -----------------------------
# Simulación de una réplica
# -----------------------------
def simulate_once(cfg: ModelConfig, servers: Dict[str, int], seed: int) -> ReplicationResult:
    """
    Simula n_customers clientes.
    Tiempo en sistema = salida - llegada (cliente espera hasta que TODO su pedido esté listo).
    """
    rng = np.random.default_rng(seed)

    # validar servers
    for st in ALL_STATIONS:
        if st not in servers:
            raise ValueError(f"Falta cantidad de servidores para estación '{st}' en servers dict.")
        if servers[st] < 1:
            raise ValueError(f"servers['{st}'] debe ser >= 1")

    # estaciones
    station_objs = {st: Station(servers[st]) for st in ALL_STATIONS}

    # distribuciones
    rv_arr = _get_rv(cfg.arrival_dist)
    rv_srv = {st: _get_rv(cfg.service_dists[st]) for st in ALL_STATIONS}

    # para elegir tipo de pedido
    probs = np.array([o.prob for o in cfg.order_types], dtype=float)
    names = [o.name for o in cfg.order_types]
    stations_by_type = [o.stations for o in cfg.order_types]

    n = cfg.settings.n_customers
    warm = cfg.settings.warmup_customers

    # acumuladores (después de warmup)
    times_in_system: List[float] = []
    queue_wait_totals: List[float] = []
    queue_wait_cashier: List[float] = []

    t_arrival = 0.0

    for i in range(n):
        # llegada (inter-arrival)
        ia = float(rv_arr.rvs(random_state=rng))
        if ia < 0:
            ia = 0.0
        t_arrival += ia

        # CAJA
        s_caja = float(rv_srv[CAJA].rvs(random_state=rng))
        if s_caja < 0:
            s_caja = 0.0

        t_cashier_done, w_cashier = station_objs[CAJA].process(t_arrival, s_caja)

        # Elegir pedido (qué estaciones extra requiere)
        idx = int(rng.choice(len(probs), p=probs))
        required_stations = stations_by_type[idx]

        # Procesar estaciones extra en paralelo (cada una tiene su propia cola)
        completion_times = [t_cashier_done]
        total_queue_wait = w_cashier

        for st in required_stations:
            # --- Binomial: cantidad de órdenes en esta estación ---
            k = int(rng.binomial(5, 2/5))

            # tiempo base de servicio
            s_base = float(rv_srv[st].rvs(random_state=rng))
            if s_base < 0:
                s_base = 0.0

            # tiempo real = base × carga del pedido
            service_time = s_base * k

            t_done, wq = station_objs[st].process(t_cashier_done, service_time)
            completion_times.append(t_done)
            total_queue_wait += wq


        t_departure = max(completion_times)
        time_in_system = t_departure - t_arrival

        # guardar solo después de warmup
        if i >= warm:
            times_in_system.append(time_in_system)
            queue_wait_totals.append(total_queue_wait)
            queue_wait_cashier.append(w_cashier)

    # métricas por estación
    per_station = {}
    for st, obj in station_objs.items():
        m = obj.m
        per_station[st] = {
            "n_jobs": float(m.n_jobs),
            "avg_queue_wait": (m.total_wait / m.n_jobs) if m.n_jobs > 0 else 0.0,
            "avg_service": (m.total_service / m.n_jobs) if m.n_jobs > 0 else 0.0,
            "last_completion": float(m.last_completion),
        }

    def _mean(x: List[float]) -> float:
        return float(np.mean(x)) if len(x) else 0.0

    return ReplicationResult(
        mean_time_in_system=_mean(times_in_system),
        mean_queue_wait_total=_mean(queue_wait_totals),
        mean_queue_wait_cashier=_mean(queue_wait_cashier),
        per_station=per_station,
        n_effective=len(times_in_system),
    )


# -----------------------------
# Varias réplicas
# -----------------------------
def run_replications(cfg: ModelConfig, servers: Dict[str, int]) -> List[ReplicationResult]:
    base_seed = cfg.settings.seed
    reps = cfg.settings.replications
    results = []
    for r in range(reps):
        results.append(simulate_once(cfg, servers, seed=base_seed + r))
    return results
