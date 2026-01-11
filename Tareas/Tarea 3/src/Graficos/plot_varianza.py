import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import chi2

BASE = Path(__file__).resolve().parents[2]   # .../Tarea 3
DATA = BASE / "Data"
OUT  = BASE / "results"
OUT.mkdir(exist_ok=True)

ALPHA = 0.05

# Archivos y su varianza teórica
FILES = [
    ("java_u01.txt",     1/12),
    ("julia_u01.txt",    1/12),
    ("python_u01.txt",   1/12),
    ("erlang_u01.txt",   1/12),
    ("python_u1_6.txt",  (6**2 - 1)/12),   # U{1..6}
    ("c_u1_4.txt",       (4**2 - 1)/12),   # U{1..4}
    ("c_u1_8.txt",       (8**2 - 1)/12),   # U{1..8}
    ("racket_u1_20.txt", (20**2 - 1)/12),  # U{1..20}
]

def plot_varianza(file_path: Path, sigma2: float, alpha=0.05):
    x = np.loadtxt(file_path)
    n = len(x)
    df = n - 1

    s2 = np.var(x, ddof=1)
    chi0 = df * s2 / sigma2

    low  = chi2.ppf(alpha/2, df)
    high = chi2.ppf(1 - alpha/2, df)

    # Curva chi-cuadrado
    left  = max(0.0, low * 0.90)
    right = high * 1.10
    xs = np.linspace(left, right, 800)
    ys = chi2.pdf(xs, df)

    plt.figure(figsize=(10, 5.6))
    plt.plot(xs, ys)

    # Líneas críticas + estadístico
    plt.axvline(low,  linestyle="--")
    plt.axvline(high, linestyle="--")
    plt.axvline(chi0)

    decision = "No se rechaza H0" if (low <= chi0 <= high) else "Se rechaza H0"

    # Texto resumen
    txt = (
        f"α={alpha}\n"
        f"n={n:,}\n"
        f"df={df:,}\n"
        f"σ₀²={sigma2:.8f}\n"
        f"s²={s2:.8f}\n"
        f"χ₀²={chi0:,.4f}\n"
        f"χ²_L={low:,.4f}\n"
        f"χ²_U={high:,.4f}\n"
        f"{decision}"
    )
    plt.text(0.02, 0.95, txt, transform=plt.gca().transAxes, va="top")

    plt.title(f"Prueba de Varianza (χ²) — {file_path.name}")
    plt.xlabel("χ²")
    plt.ylabel("densidad")
    plt.tight_layout()

    out = OUT / f"{file_path.stem}_varianza.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print("OK:", out)

if __name__ == "__main__":
    for name, sigma2 in FILES:
        f = DATA / name
        if f.exists():
            plot_varianza(f, sigma2, ALPHA)
        else:
            print("NO EXISTE:", f)