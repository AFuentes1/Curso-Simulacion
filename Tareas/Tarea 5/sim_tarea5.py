import heapq
import math
import random
from dataclasses import dataclass, field
from typing import Callable

# =====================================================
# Distribuciones de servicio (minutos)
# =====================================================

def exp_mean(mean: float) -> float:
    return random.expovariate(1.0 / mean)

def binomial(n: int, p: float) -> int:
    return sum(1 for _ in range(n) if random.random() < p)

def geometric(p: float) -> int:
    u = random.random()
    return int(math.ceil(math.log(1 - u) / math.log(1 - p)))

def normal_discrete(mean: float, sd: float) -> int:
    return max(0, int(round(random.gauss(mean, sd))))

# =====================================================
# Proceso de llegadas (Poisson no homogéneo)
# =====================================================

class ArrivalProcess:
    """
    Proceso de llegadas con λ(t) variable.
    λ(t) se define en clientes / hora.
    """

    def __init__(self, lambda_func: Callable[[float], float]):
        self.lambda_func = lambda_func

    def next_interarrival(self, t_min: float) -> float:
        """
        Genera el próximo interarribo dado el tiempo actual.
        t_min: tiempo actual en minutos.
        """
        t_hours = t_min / 60.0
        lam_h = self.lambda_func(t_hours)

        if lam_h <= 0:
            return float("inf")

        lam_min = lam_h / 60.0
        return random.expovariate(lam_min)

# =====================================================
# Estructuras
# =====================================================

@dataclass
class Client:
    cid: int
    arrival_time: float
    route: list
    idx: int = 0

@dataclass
class Station:
    key: str
    servers: int
    service_sampler: Callable[[], float]
    queue: list = field(default_factory=list)
    busy: int = 0
    busy_area: float = 0.0
    last_t: float = 0.0

    def update_area(self, t: float):
        self.busy_area += self.busy * (t - self.last_t)
        self.last_t = t

# =====================================================
# Eventos
# =====================================================

ARRIVAL = "ARRIVAL"
ENTER   = "ENTER"
DEPART  = "DEPART"

# =====================================================
# Simulación
# =====================================================

def simulate(
    config: dict,
    arrival_process: ArrivalProcess,
    seed: int = 123,
    T_hours: float = 8.0,
    normal_sd: float = 1.0,
    p_ref: float = 0.9,
    p_frei: float = 0.7,
    p_pos: float = 0.25,
    p_pol: float = 0.3,
    orders_n: int = 5,
    orders_p: float = 2 / 5,
):
    random.seed(seed)

    T = T_hours * 60.0  # minutos

    stations = {
        "cajas": Station("cajas", config["cajas"], lambda: exp_mean(2.5)),
        "ref":   Station("ref",   config["ref"],   lambda: exp_mean(0.75)),
        "frei":  Station("frei",  config["frei"],  lambda: float(normal_discrete(3.0, normal_sd))),
        "pos":   Station("pos",   config["pos"],   lambda: float(binomial(5, 0.6))),
        "pol":   Station("pol",   config["pol"],   lambda: float(geometric(0.1))),
    }

    event_q = []
    ec = 0

    def schedule(time, etype, st_key, client):
        nonlocal ec
        heapq.heappush(event_q, (time, ec, etype, st_key, client))
        ec += 1

    def make_route():
        route = ["cajas"]
        if random.random() < p_ref:  route.append("ref")
        if random.random() < p_frei: route.append("frei")
        if random.random() < p_pos:  route.append("pos")
        if random.random() < p_pol:  route.append("pol")
        return route

    def start_service(st: Station, t: float):
        _, client = st.queue.pop(0)
        st.update_area(t)
        st.busy += 1

        k = max(1, binomial(orders_n, orders_p))
        service_time = st.service_sampler() * k
        schedule(t + service_time, DEPART, st.key, client)

    # Evento inicial
    cid = 0
    schedule(0.0, ARRIVAL, None, None)

    completed_W = []

    # Loop principal
    while event_q:
        t, _, etype, st_key, client = heapq.heappop(event_q)
        if t > T:
            break

        if etype == ARRIVAL:
            c = Client(cid=cid, arrival_time=t, route=make_route())
            cid += 1

            t_next = t + arrival_process.next_interarrival(t)
            if t_next <= T:
                schedule(t_next, ARRIVAL, None, None)

            schedule(t, ENTER, "cajas", c)

        elif etype == ENTER:
            st = stations[st_key]
            st.update_area(t)
            st.queue.append((t, client))
            if st.busy < st.servers:
                start_service(st, t)

        elif etype == DEPART:
            st = stations[st_key]
            st.update_area(t)
            st.busy -= 1

            client.idx += 1
            if client.idx >= len(client.route):
                completed_W.append(t - client.arrival_time)
            else:
                schedule(t, ENTER, client.route[client.idx], client)

            if st.queue and st.busy < st.servers:
                start_service(st, t)

    for st in stations.values():
        st.update_area(T)

    if completed_W:
        W_avg = sum(completed_W) / len(completed_W)
        W_var = sum((w - W_avg) ** 2 for w in completed_W) / len(completed_W)
    else:
        W_avg = float("nan")
        W_var = float("nan")

    rho = {
        k: stations[k].busy_area / (T * max(1, stations[k].servers))
        for k in stations
    }

    return len(completed_W), W_avg, W_var, rho

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    def lambda_shift(t):
        return 3.0

    arrival = ArrivalProcess(lambda_shift)

    configs = {
        "MIN_W":   {"cajas": 2, "ref": 1, "frei": 4, "pos": 2, "pol": 3},
        "MIN_VAR": {"cajas": 2, "ref": 2, "frei": 2, "pos": 3, "pol": 3},
    }

    R = 50

    for name, cfg in configs.items():
        Ws, Vs = [], []
        rho_acc = {k: 0.0 for k in cfg}

        for s in range(R):
            _, W_avg, W_var, rho = simulate(
                config=cfg,
                arrival_process=arrival,
                seed=2000 + s,
                T_hours=8.0,
            )
            Ws.append(W_avg)
            Vs.append(W_var)
            for k in rho_acc:
                rho_acc[k] += rho[k]

        for k in rho_acc:
            rho_acc[k] /= R

        print("\n", name, cfg)
        print("W_prom:", sum(Ws) / R)
        print("VarW_prom:", sum(Vs) / R)
        print("rho_prom:", rho_acc)
