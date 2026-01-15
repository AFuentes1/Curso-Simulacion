import heapq
import math
import random
from dataclasses import dataclass, field

# -------------------------
# Distribuciones (minutos)
# -------------------------
def exp_mean(mean: float) -> float:
    return random.expovariate(1.0 / mean)

def binomial(n: int, p: float) -> int:
    return sum(1 for _ in range(n) if random.random() < p)

def geometric(p: float) -> int:
    # soporte 1,2,3,... (minutos)
    u = random.random()
    return int(math.ceil(math.log(1 - u) / math.log(1 - p)))

def normal_discrete(mean: float, sd: float) -> int:
    return max(0, int(round(random.gauss(mean, sd))))

# -------------------------
# Estructuras
# -------------------------
@dataclass
class Client:
    cid: int
    arrival_time: float
    route: list
    idx: int = 0  # estación actual en la ruta

@dataclass
class Station:
    key: str
    servers: int
    service_sampler: callable
    queue: list = field(default_factory=list)  # (t_llegada_a_cola, client)
    busy: int = 0
    busy_area: float = 0.0
    last_t: float = 0.0

    def update_area(self, t: float):
        self.busy_area += self.busy * (t - self.last_t)
        self.last_t = t

# -------------------------
# Simulación (DES)
# -------------------------
ARRIVAL = "ARRIVAL"
ENTER   = "ENTER"
DEPART  = "DEPART"

def simulate(
    config,
    seed=123,
    T=480.0,
    lam_per_min=3.0,     # si λ es por HORA => usar 3/60
    normal_sd=1.0,       # si el enunciado da SD, ponelo aquí
    p_ref=0.9,
    p_frei=0.7,
    p_pos=0.25,
    p_pol=0.3,
    orders_n=5,
    orders_p=2/5
):
    random.seed(seed)

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

    def next_interarrival():
        return random.expovariate(lam_per_min)

    def make_route():
        route = ["cajas"]
        if random.random() < p_ref:  route.append("ref")
        if random.random() < p_frei: route.append("frei")
        if random.random() < p_pos:  route.append("pos")
        if random.random() < p_pol:  route.append("pol")
        return route

    def start_service(st: Station, t: float):
        # FCFS
        _, client = st.queue.pop(0)
        st.update_area(t)
        st.busy += 1

        # "cantidad de órdenes" (binomial). Evitamos 0.
        k = binomial(orders_n, orders_p)
        k = max(1, k)

        service_time = st.service_sampler() * k
        schedule(t + service_time, DEPART, st.key, client)

    # primer arribo
    t0 = 0.0
    cid = 0
    schedule(t0, ARRIVAL, None, None)

    completed_W = []

    while event_q:
        t, _, etype, st_key, client = heapq.heappop(event_q)
        if t > T:
            break

        if etype == ARRIVAL:
            c = Client(cid=cid, arrival_time=t, route=make_route())
            cid += 1

            t_next = t + next_interarrival()
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

            # cliente sigue ruta o sale del sistema
            client.idx += 1
            if client.idx >= len(client.route):
                completed_W.append(t - client.arrival_time)
            else:
                nxt = client.route[client.idx]
                schedule(t, ENTER, nxt, client)

            # si hay cola, arranca otro
            if st.queue and st.busy < st.servers:
                start_service(st, t)

    # cerrar áreas a T
    for st in stations.values():
        st.update_area(T)

    if completed_W:
        W_avg = sum(completed_W) / len(completed_W)
        W_var = sum((w - W_avg) ** 2 for w in completed_W) / len(completed_W)
    else:
        W_avg = float("nan")
        W_var = float("nan")

    rho = {
        k: (stations[k].busy_area / (T * max(1, stations[k].servers)))
        for k in stations.keys()
    }

    return len(completed_W), W_avg, W_var, rho

if __name__ == "__main__":
    R = 50

    configs = {
        "MIN_W":   {"cajas": 2, "ref": 1, "frei": 4, "pos": 2, "pol": 3},
        "MIN_VAR": {"cajas": 2, "ref": 2, "frei": 2, "pos": 3, "pol": 3},
    }

    for name, cfg in configs.items():
        Ws, Vs = [], []
        rho_acc = {"cajas": 0.0, "ref": 0.0, "frei": 0.0, "pos": 0.0, "pol": 0.0}

        for s in range(R):
            n, W_avg, W_var, rho = simulate(
                config=cfg,
                seed=2000 + s,
                T=480.0,
                lam_per_min=3/60,
                normal_sd=1.0
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