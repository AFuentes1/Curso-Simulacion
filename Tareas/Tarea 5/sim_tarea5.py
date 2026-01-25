import csv
import heapq
import math
import random
from dataclasses import dataclass, field
from itertools import combinations_with_replacement, permutations
import os

# =========================
# Distribuciones (minutos)
# =========================

def exp_mean(mean):
    return random.expovariate(1.0 / mean)

def binomial(n, p):
    return sum(1 for _ in range(n) if random.random() < p)

def geometric(p):
    u = random.random()
    return int(math.ceil(math.log(1 - u) / math.log(1 - p)))

def normal_discrete(mean, sd):
    return max(0, int(round(random.gauss(mean, sd))))

# =========================
# Estructuras
# =========================

@dataclass
class Client:
    cid: int
    arrival_time: float

    stage1_end: float = 0.0
    stage2_end: float = 0.0
    pending: int = 0

    wait_time: float = 0.0
    service_time: float = 0.0

@dataclass
class Job:
    client: Client
    arrival_to_queue: float

@dataclass
class Station:
    key: str
    servers: int
    service_sampler: callable
    queue: list = field(default_factory=list)
    busy: int = 0
    busy_area: float = 0.0
    last_t: float = 0.0

    def update_area(self, t):
        self.busy_area += self.busy * (t - self.last_t)
        self.last_t = t

# =========================
# Eventos
# =========================

ARRIVAL = "ARRIVAL"
ENTER   = "ENTER"
DEPART  = "DEPART"

# =========================
# Simulación DES
# =========================
def simulate(
    config,
    seed=123,
    T=480.0,          # minutos
    lam=3.0,          # llegadas de clientes
    normal_sd=1.0,
    p_ref=0.9,
    p_frei=0.7,
    p_pos=0.25,
    p_pol=0.3,
    orders_n=5,
    orders_p=2/5
):
    random.seed(seed)

    # =========================
    # ESTACIONES
    # =========================
    stations = {
        "cajas": Station("cajas", config["cajas"], lambda: exp_mean(2.5)),
        "ref":   Station("ref",   config["ref"],   lambda: exp_mean(0.75)),
        "frei":  Station("frei",  config["frei"],  lambda: normal_discrete(3.0, normal_sd)),
        "pos":   Station("pos",   config["pos"],   lambda: binomial(5, 0.6)),
        "pol":   Station("pol",   config["pol"],   lambda: geometric(0.1)),
    }

    # inicializar servidores individuales
    for st in stations.values():
        st.jobs_in = 0
        st.free_servers = list(range(1, st.servers + 1))
        st.busy = 0

    # =========================
    # EVENT LOG (LO QUE TÚ QUIERES)
    # =========================
    event_log = []

    # =========================
    # EVENTOS
    # =========================
    event_q = []
    ec = 0

    def schedule(t, etype, st, obj):
        nonlocal ec
        heapq.heappush(event_q, (t, ec, etype, st, obj))
        ec += 1

    def next_interarrival():
        return random.expovariate(lam)

    def start_service(st, t):
        job = st.queue.pop(0)
        server_id = st.free_servers.pop(0)

        st.update_area(t)
        st.busy += 1

        start_time = t
        service_time = st.service_sampler()
        end_time = t + service_time

        # tiempo en cola
        job.client.wait_time += start_time - job.arrival_to_queue
        job.client.service_time += service_time

        # ===== TRACE EXACTO =====
        event_log.append({
            "estacion": st.key,
            "hora_llegada": job.arrival_to_queue,
            "hora_inicio": start_time,
            "servidor": server_id,
            "tiempo_atencion": service_time,
            "hora_fin": end_time
        })

        schedule(end_time, DEPART, st.key, (job, server_id))

    # =========================
    # SIMULACIÓN
    # =========================
    cid = 0
    schedule(0.0, ARRIVAL, None, None)

    completed = []

    while event_q:
        t, _, etype, st_key, obj = heapq.heappop(event_q)
        if t > T:
            break

        # -------------------------
        # LLEGADA DE CLIENTE
        # -------------------------
        if etype == ARRIVAL:
            c = Client(cid=cid, arrival_time=t)
            cid += 1

            t_next = t + next_interarrival()
            if t_next <= T:
                schedule(t_next, ARRIVAL, None, None)

            schedule(t, ENTER, "cajas", Job(c, t))

        # -------------------------
        # ENTRADA A ESTACIÓN
        # -------------------------
        elif etype == ENTER:
            st = stations[st_key]
            st.update_area(t)

            st.jobs_in += 1
            st.queue.append(obj)

            if st.free_servers:
                start_service(st, t)

        # -------------------------
        # SALIDA DE ESTACIÓN
        # -------------------------
        elif etype == DEPART:
            st = stations[st_key]
            st.update_area(t)
            st.busy -= 1

            job, server_id = obj
            st.free_servers.append(server_id)

            c = job.client

            # ===== ETAPA 1 → ETAPA 2 =====
            if st.key == "cajas":
                c.stage1_end = t
                k = binomial(orders_n, orders_p)

                if k > 0:
                    for key, p in (("ref", p_ref), ("frei", p_frei), ("pos", p_pos), ("pol", p_pol)):
                        if random.random() < p:
                            c.pending += k
                            for _ in range(k):
                                schedule(t, ENTER, key, Job(c, t))
                

                if c.pending == 0:
                    c.stage2_end = t
                    completed.append(c)

            # ===== ETAPA 2 =====
            else:
                c.pending -= 1
                c.stage2_end = max(c.stage2_end, t)

                if c.pending == 0:
                    completed.append(c)

            if st.queue and st.free_servers:
                start_service(st, t)

    # =========================
    # CIERRE DE ÁREAS
    # =========================
    for st in stations.values():
        st.update_area(T)

    # =========================
    # MÉTRICAS
    # =========================
    stats = {}

    if completed:
        W_sys = [c.stage2_end - c.arrival_time for c in completed]
        W_wait = [c.wait_time for c in completed]
        W_serv = [c.service_time for c in completed]

        mean_W = sum(W_sys) / len(W_sys)
        var_W  = sum((w - mean_W) ** 2 for w in W_sys) / len(W_sys)

        throughput = len(completed) / T   # clientes / minuto

        stats.update({
            "W_sys_avg": mean_W,
            "W_wait_avg": sum(W_wait) / len(W_wait),
            "W_serv_avg": sum(W_serv) / len(W_serv),
            "W_sys_var": var_W,
            "throughput": throughput,
            "clients_completed": len(completed)
        })

    rho = {
        k: stations[k].busy_area / (T * max(1, stations[k].servers))
        for k in stations
    }

    lambda_hat = {
        k: stations[k].jobs_in / T
        for k in stations
    }

    throughput_jobs = lambda_hat.copy()

    return stats, rho, lambda_hat, throughput_jobs, event_log

def W_analitico(cfg):
    # parámetros del PDF
    lam = 3.0

    probs = {
        "cajas": 1.0,
        "ref": 0.9,
        "frei": 0.7,
        "pos": 0.25,
        "pol": 0.3
    }

    mu = {
        "cajas": 1 / 2.5,
        "ref":   1 / 0.75,
        "frei":  1 / 3.0,
        "pos":   1 / 3.0,
        "pol":   1 / 10.0
    }

    W = 0.0
    rho_vals = {}

    for k in probs:
        lam_i = lam * probs[k]
        c = cfg[k]
        mu_i = mu[k]

        rho = lam_i / (c * mu_i)
        rho_vals[k] = rho

        if rho >= 1:
            continue  # sistema inestable, ignorar

        W_i = (rho / (mu_i * (1 - rho))) + (1 / mu_i)
        W += probs[k] * W_i

    return W, rho_vals

def check_rho(rho_dict, threshold=0.8):
    violaciones = {}
    for k, v in rho_dict.items():
        violaciones[k] = (v >= threshold)
    return violaciones

# =========================
# Main
# =========================
if __name__ == "__main__":

    R = 2        # réplicas por configuración
    T = 480.0       # minutos
    lam = 3.0       # clientes / minuto

    # ==================================================
    # GENERAR CONFIGURACIONES VÁLIDAS
    # ==================================================
    configs = []

    for combo in combinations_with_replacement(range(8), 5):
        if sum(combo) == 7:
            for perm in set(permutations(combo)):
                cfg = tuple(x + 1 for x in perm)
                if cfg[0] >= 1:  # al menos 1 servidor en cajas
                    configs.append(cfg)

    print(f"Configuraciones válidas: {len(configs)}")

    # ==================================================
    # CARPETA RAÍZ PARA TODAS LAS TABLAS
    # ==================================================
    BASE_DIR = "tablas"
    os.makedirs(BASE_DIR, exist_ok=True)


    # ==================================================
    # SIMULACIÓN POR CONFIGURACIÓN
    # ==================================================
    results = []

    for idx, cfg in enumerate(configs, start=1):

        cfg_dict = {
            "cajas": cfg[0],
            "ref":   cfg[1],
            "frei":  cfg[2],
            "pos":   cfg[3],
            "pol":   cfg[4],
        }

        # ==================================================
        # CARPETA PARA ESTA CONFIGURACIÓN
        # ==================================================
        cfg_name = f"cfg_c{cfg[0]}_r{cfg[1]}_f{cfg[2]}_p{cfg[3]}_l{cfg[4]}"
        cfg_dir = os.path.join(BASE_DIR, cfg_name)
        os.makedirs(cfg_dir, exist_ok=True)


        W_means = []
        W_vars  = []
        throughput_means  = []

        rho_acc = {k: 0.0 for k in cfg_dict}
        jobs_acc = {k: 0 for k in cfg_dict}
        clients_acc = 0
        # ============================================
        # ACUMULAR EVENTOS DE TODAS LAS RÉPLICAS
        # ============================================
        


        for r in range(R):
            stats, rho, lambda_hat_rep, throughput_jobs, event_log = simulate(
                config=cfg_dict,
                seed=100000 * idx + r,
                T=T,
                lam=lam
            )

            eventos_I = []    # solo cajas
            eventos_II = []   # ref, frei, pos, pol


            for e in event_log:
                fila_base = [
                    round(e["hora_llegada"], 4),
                    round(e["hora_inicio"], 4),
                    e["servidor"],
                    round(e["tiempo_atencion"], 4),
                    round(e["hora_fin"] - e["hora_llegada"], 4),
                    round(e["hora_fin"], 4)
                ]

                if e["estacion"] == "cajas":
                    eventos_I.append(fila_base)
                else:
                    eventos_II.append([e["estacion"]] + fila_base)





            W_means.append(stats["W_sys_avg"])
            W_vars.append(stats["W_sys_var"])
            throughput_means .append(stats["throughput"])

            for k in rho_acc:
                rho_acc[k] += rho[k]
                jobs_acc[k] += throughput_jobs[k]

            clients_acc += stats["clients_completed"]
        
        with open(
            os.path.join(cfg_dir, f"etapa_I_{r+1}.csv"),
            "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow([
                "Hora_llegada",
                "Hora_inicio_atencion",
                "Servidor",
                "Tiempo_atencion",
                "Tiempo_sistema_1",
                "Hora_fin"
            ])
            writer.writerows(eventos_I)


        
        with open(
            os.path.join(cfg_dir, f"etapa_II_{r+1}.csv"),
            "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow([
                "Estacion",
                "Hora_llegada",
                "Hora_inicio_atencion",
                "Servidor",
                "Tiempo_atencion",
                "Tiempo_sistema_2",
                "Hora_fin"
            ])
            writer.writerows(eventos_II)

        # =========================
        # PROMEDIOS
        # =========================
        W_mean = sum(W_means) / R
        Var_W  = sum(W_vars) / R
        throughput_mean = sum(throughput_means ) / R

        # IC 95% para W̄
        if R > 1:
            s = math.sqrt(sum((w - W_mean)**2 for w in W_means) / (R - 1))
            IC_low  = W_mean - 1.96 * s / math.sqrt(R)
            IC_high = W_mean + 1.96 * s / math.sqrt(R)
        else:
            IC_low = IC_high = W_mean

        rho_sim = {k: rho_acc[k] / R for k in rho_acc}

        # λ̂ᵢ efectivo
        lambda_hat = {k: jobs_acc[k] / (R * T) for k in jobs_acc}


        # analítico (solo referencia)
        W_an, rho_an = W_analitico(cfg_dict)

        viol_sim = check_rho(rho_sim)
        viol_an  = check_rho(rho_an)
        n_viol = sum(1 for k in cfg_dict if viol_sim[k] or viol_an[k])

        results.append({
            "config": cfg,
            "W_sys": W_mean,
            "throughput": throughput_mean,
            "servers_total": sum(cfg),   # todos son humanos en tu modelo
            "Var_W": Var_W,
            "IC": (IC_low, IC_high),
            "W_an": W_an,
            "rho": rho_sim,
            "lambda_hat": lambda_hat,
            "viol": n_viol,
            "clients": clients_acc / R
        })


        print(
            f"[{idx:3d}/{len(configs)}] "
            f"cfg={cfg}  W̄={W_mean:.3f}  Var(W)={Var_W:.3f}  viol={n_viol}"
        )



    # ==================================================
    # ÓPTIMOS (DOS PROBLEMAS DISTINTOS)
    # ==================================================
    best_W = min(
        results,
        key=lambda r: (r["throughput"], r["servers_total"])
    )

    best_VAR = min(results, key=lambda r: r["Var_W"])

    print("\n==============================================")
    print("CONFIGURACIONES ÓPTIMAS")
    print("==============================================")

    print("\nMIN_W (minimiza throughput = T / clientes)")
    print(f"cfg={best_W['config']}  throughput={best_W['throughput']:.4f}  "
          f"W̄_real={best_W['W_sys']:.4f}  "
          f"IC95%=[{best_W['IC'][0]:.4f},{best_W['IC'][1]:.4f}]")


    print("\nMIN_VAR (minimiza Var(W))")
    print(f"cfg={best_VAR['config']}  Var(W)={best_VAR['Var_W']:.4f}  "
          f"W̄={best_VAR['W_sys']:.4f}")
    
    # ==================================================
    # MINI-TABLA λ̂ᵢ vs λ·pᵢ·E[K] (PARA REPORTE)
    # ==================================================

    # Parámetros teóricos
    p_visita = {
        "cajas": 1.0,
        "ref":   0.9,
        "frei":  0.7,
        "pos":   0.25,
        "pol":   0.3
    }

    E_K = {
        "cajas": 1.0,   # siempre 1 paso por cajas
        "ref":   2.0,   # Binomial(5, 2/5)
        "frei":  2.0,
        "pos":   2.0,
        "pol":   2.0
    }

    lambda_cliente = lam  # clientes / min

    print("\n==============================================")
    print("λ̂ᵢ vs λ · pᵢ · E[K]  (Configuración MIN_W)")
    print("==============================================")
    print(f"{'Estación':<10}{'λ̂ᵢ sim':>12}{'λ·pᵢ·E[K]':>15}{'Ratio':>10}")
    print("-" * 50)

    lambda_hat_sim = best_W["lambda_hat"]

    for k in ["cajas", "ref", "frei", "pos", "pol"]:
        lambda_teo = lambda_cliente * p_visita[k] * E_K[k]
        lambda_sim = lambda_hat_sim[k]

        ratio = lambda_sim / lambda_teo if lambda_teo > 0 else float("nan")

        print(f"{k:<10}{lambda_sim:>12.4f}{lambda_teo:>15.4f}{ratio:>10.3f}")


    # ==================================================
    # EXPORTAR MINI-TABLA λ̂ᵢ vs λ · pᵢ · E[K] (MIN_W)
    # ==================================================

    p_visita = {
        "cajas": 1.0,
        "ref":   0.9,
        "frei":  0.7,
        "pos":   0.25,
        "pol":   0.3
    }

    E_K = {
        "cajas": 1.0,
        "ref":   2.0,   # Binomial(5, 2/5)
        "frei":  2.0,
        "pos":   2.0,
        "pol":   2.0
    }

    lambda_cliente = lam  # clientes / minuto
    lambda_hat_sim = best_W["lambda_hat"]

    csv_lambda = "lambda_hat_vs_teorico_MIN_W.csv"

    with open(csv_lambda, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "estacion",
            "lambda_hat_sim",
            "lambda_teorico_lpEK",
            "ratio_sim_teorico"
        ])

        for k in ["cajas", "ref", "frei", "pos", "pol"]:
            lambda_teo = lambda_cliente * p_visita[k] * E_K[k]
            lambda_sim = lambda_hat_sim[k]

            ratio = lambda_sim / lambda_teo if lambda_teo > 0 else ""

            writer.writerow([
                k,
                round(lambda_sim, 6),
                round(lambda_teo, 6),
                round(ratio, 4) if ratio != "" else ""
            ])

    print(f"\nMini-tabla λ̂ᵢ vs λ·pᵢ·E[K] exportada a '{csv_lambda}'")

    # ==================================================
    # EXPORTAR MINI-TABLA λ̂ᵢ vs λ · pᵢ · E[K] (MIN_VAR)
    # ==================================================

    p_visita = {
        "cajas": 1.0,
        "ref":   0.9,
        "frei":  0.7,
        "pos":   0.25,
        "pol":   0.3
    }

    E_K = {
        "cajas": 1.0,
        "ref":   2.0,   # Binomial(5, 2/5)
        "frei":  2.0,
        "pos":   2.0,
        "pol":   2.0
    }

    lambda_cliente = lam  # clientes / minuto
    lambda_hat_sim = best_VAR["lambda_hat"]

    csv_lambda = "lambda_hat_vs_teorico_MIN_VAR.csv"

    with open(csv_lambda, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "estacion",
            "lambda_hat_sim",
            "lambda_teorico_lpEK",
            "ratio_sim_teorico"
        ])

        for k in ["cajas", "ref", "frei", "pos", "pol"]:
            lambda_teo = lambda_cliente * p_visita[k] * E_K[k]
            lambda_sim = lambda_hat_sim[k]

            ratio = lambda_sim / lambda_teo if lambda_teo > 0 else ""

            writer.writerow([
                k,
                round(lambda_sim, 6),
                round(lambda_teo, 6),
                round(ratio, 4) if ratio != "" else ""
            ])

    print(f"\nMini-tabla λ̂ᵢ vs λ·pᵢ·E[K] (MIN_VAR) exportada a '{csv_lambda}'")


    # ==================================================
    # EXPORTAR CSV
    # ==================================================
    with open("resultados_todas_configuraciones.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "cajas","ref","frei","pos","pol",
            "W_sim","throughput","Var_W","IC_low","IC_high",
            "W_analitico_ref",
            "clientes_completados",
            "viol_rho",
            "criterio_optimo"
        ])




        for r in results:
            cfg = r["config"]
            criterio = ""
            if cfg == best_W["config"]:
                criterio = "MIN_W"
            elif cfg == best_VAR["config"]:
                criterio = "MIN_VAR"

            writer.writerow([
                *cfg,
                round(r["W_sys"],4),
                round(r["throughput"],4),
                round(r["Var_W"],4),
                round(r["IC"][0],4),
                round(r["IC"][1],4),
                round(r["W_an"],4),
                round(r["clients"],2),
                r["viol"],
                criterio
            ])


    print("\nCSV generado: resultados_todas_configuraciones.csv")
