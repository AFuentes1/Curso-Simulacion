import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from pathlib import Path

def params_uniform(kind, a, b):
    if kind == "continuous":
        mu = (a + b) / 2
        sigma2 = ((b - a) ** 2) / 12
    else:
        m = int(b - a + 1)
        mu = (a + b) / 2
        sigma2 = (m**2 - 1) / 12
    return mu, sigma2

def plot_promedio(file_path, kind="continuous", a=0, b=1, alpha=0.05, out_dir="results"):
    x = np.loadtxt(file_path)
    n = x.size

    mu, sigma2 = params_uniform(kind, a, b)
    xbar = x.mean()

    z0 = (xbar - mu) / np.sqrt(sigma2 / n)
    zcrit = norm.ppf(1 - alpha/2)
    decision = "No se rechaza H0" if abs(z0) <= zcrit else "Se rechaza H0"

    z = np.linspace(-4, 4, 400)
    pdf = norm.pdf(z)

    plt.figure(figsize=(9, 5))
    plt.plot(z, pdf, linewidth=2)
    plt.axvline(-zcrit, linestyle="--", linewidth=2)
    plt.axvline( zcrit, linestyle="--", linewidth=2)
    plt.axvline(z0, linewidth=2)

    title = f"Prueba de la Media (Z) — {Path(file_path).name}"
    plt.title(title)
    plt.xlabel("z")
    plt.ylabel("densidad")
    plt.text(-3.4, 0.35, f"alpha={alpha}\n z0={z0:.4f}\n zcrit=±{zcrit:.4f}\n{decision}")

    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"{Path(file_path).stem}_promedio.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=200)
    plt.close()

    print(f"[OK] {Path(file_path).name} -> {out_file}")

if __name__ == "__main__":
    BASE = Path(__file__).resolve().parents[2]   # .../Tarea 3
    DATA = BASE / "Data"
    OUT  = BASE / "results"

    muestras = [
        # continuas [0,1)
        ("java_u01.txt",   "continuous", 0, 1),
        ("julia_u01.txt",  "continuous", 0, 1),
        ("python_u01.txt", "continuous", 0, 1),
        ("erlang_u01.txt", "continuous", 0, 1),

        # discretas
        ("python_u1_6.txt","discrete",   1, 6),
        ("c_u1_4.txt",     "discrete",   1, 4),
        ("c_u1_8.txt",     "discrete",   1, 8),
        ("racket_u1_20.txt","discrete",  1, 20),
    ]

    for fname, kind, a, b in muestras:
        f = DATA / fname
        if f.exists():
            plot_promedio(str(f), kind=kind, a=a, b=b, alpha=0.05, out_dir=str(OUT))
        else:
            print(f"[SKIP] No existe: {f}")