#Prueba promedio para todos 
import numpy as np
from scipy.stats import norm
from pathlib import Path

def params_uniform(kind, a, b):
    # kind: "continuous" para U(a,b) real, "discrete" para uniforme entera {a,...,b}
    if kind == "continuous":
        mu = (a + b) / 2
        sigma2 = ((b - a) ** 2) / 12
        return mu, sigma2
    else:
        m = int(b - a + 1)
        mu = (a + b) / 2
        sigma2 = (m**2 - 1) / 12
        return mu, sigma2

def prueba_promedio(path, kind="continuous", a=0, b=1, alpha=0.05):
    x = np.loadtxt(path)  # sirve para float o int
    n = x.size

    mu, sigma2 = params_uniform(kind, a, b)
    xbar = x.mean()

    zcrit = norm.ppf(1 - alpha/2)
    half = zcrit * np.sqrt(sigma2 / n)
    low, high = mu - half, mu + half

    pasa = (low <= xbar <= high)

    return pasa, {
        "n": int(n),
        "xbar": float(xbar),
        "mu": float(mu),
        "sigma2": float(sigma2),
        "alpha": float(alpha),
        "intervalo": [float(low), float(high)]
    }

if __name__ == "__main__":
    # Ajustá si tu carpeta se llama distinto (Data vs data)
    DATA = Path(__file__).resolve().parents[2] / "Data"

    # (archivo, kind, a, b)
    casos = [
        ("java_u01.txt",    "continuous", 0, 1),
        ("julia_u01.txt",   "continuous", 0, 1),
        ("python_u01.txt",  "continuous", 0, 1),
        ("erlang_u01.txt",  "continuous", 0, 1),

        ("python_u1_6.txt", "discrete",   1, 6),
        ("c_u1_4.txt",      "discrete",   1, 4),
        ("c_u1_8.txt",      "discrete",   1, 8),
        ("racket_u1_20.txt","discrete",   1, 20),
    ]

    alpha = 0.05

    print("=== PRUEBA DE PROMEDIO (alpha=0.05) ===\n")
    for fname, kind, a, b in casos:
        f = DATA / fname
        if not f.exists():
            print(f"[NO EXISTE] {fname}")
            continue

        pasa, info = prueba_promedio(str(f), kind=kind, a=a, b=b, alpha=alpha)
        low, high = info["intervalo"]
        print(f"{fname:15} | {kind:10} [{a},{b}] | PASA: {pasa}")
        print(f"  n={info['n']}  x̄={info['xbar']:.12f}  μ={info['mu']:.6f}")
        print(f"  intervalo: [{low:.12f}, {high:.12f}]\n")