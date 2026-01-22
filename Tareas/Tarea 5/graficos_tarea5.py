import matplotlib.pyplot as plt
from sim_tarea5 import simulate  # importa tu simulador

R = 50
T = 480.0
LAM = 3/60
SD  = 1.0

CONFIGS = {
    "MIN_W":   {"cajas": 2, "ref": 1, "frei": 4, "pos": 2, "pol": 3},
    "MIN_VAR": {"cajas": 2, "ref": 2, "frei": 2, "pos": 3, "pol": 3},
}

def run_replications(cfg, seed0=2000):
    Ws, Vs = [], []
    rho_acc = {"cajas":0.0, "ref":0.0, "frei":0.0, "pos":0.0, "pol":0.0}

    for s in range(R):
        n, W_avg, W_var, rho = simulate(
            config=cfg,
            seed=seed0 + s,
            T=T,
            lam_per_min=LAM,
            normal_sd=SD
        )
        Ws.append(W_avg)
        Vs.append(W_var)
        for k in rho_acc:
            rho_acc[k] += rho[k]

    for k in rho_acc:
        rho_acc[k] /= R

    return Ws, Vs, rho_acc

def main():
    results = {}
    for name, cfg in CONFIGS.items():
        Ws, Vs, rho = run_replications(cfg, seed0=2000 if name=="MIN_W" else 3000)
        results[name] = {"Ws": Ws, "Vs": Vs, "rho": rho}

        print("\n", name, cfg)
        print("W_prom:", sum(Ws)/R)
        print("VarW_prom:", sum(Vs)/R)
        print("rho_prom:", rho)

    # 1) Boxplot de W (comparación)
    plt.figure()
    plt.boxplot([results["MIN_W"]["Ws"], results["MIN_VAR"]["Ws"]], labels=["MIN_W", "MIN_VAR"])
    plt.ylabel("W promedio por corrida (min)")
    plt.title("Comparación de W (50 corridas)")
    plt.tight_layout()
    plt.savefig("boxplot_W.png", dpi=200)

    # 2) Boxplot de Var(W) (comparación)
    plt.figure()
    plt.boxplot([results["MIN_W"]["Vs"], results["MIN_VAR"]["Vs"]], labels=["MIN_W", "MIN_VAR"])
    plt.ylabel("Var(W) por corrida")
    plt.title("Comparación de Var(W) (50 corridas)")
    plt.tight_layout()
    plt.savefig("boxplot_VarW.png", dpi=200)

    # 3) Barras de rho promedio por estación (dos configs)
    estaciones = ["cajas", "ref", "frei", "pos", "pol"]
    rho1 = [results["MIN_W"]["rho"][k] for k in estaciones]
    rho2 = [results["MIN_VAR"]["rho"][k] for k in estaciones]

    x = range(len(estaciones))
    plt.figure()
    plt.bar([i - 0.2 for i in x], rho1, width=0.4, label="MIN_W")
    plt.bar([i + 0.2 for i in x], rho2, width=0.4, label="MIN_VAR")
    plt.axhline(0.8, linestyle="--", label="Límite 0.8")
    plt.xticks(list(x), estaciones)
    plt.ylabel("Utilización ρ promedio")
    plt.title("Utilización promedio por estación (50 corridas)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("rho_por_estacion.png", dpi=200)

    print("\nListo: boxplot_W.png, boxplot_VarW.png, rho_por_estacion.png")

if __name__ == "__main__":
    main()