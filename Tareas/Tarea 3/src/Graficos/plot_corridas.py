import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math

# --- Rutas (si el archivo está en: Tarea 3/src/Graficos/plot_corridas.py) ---
ROOT = Path(__file__).resolve().parents[2]     # .../Tarea 3
DATA = ROOT / "Data"
OUT  = ROOT / "results"
OUT.mkdir(exist_ok=True)

def phi(z):  # densidad N(0,1)
    return (1 / math.sqrt(2*math.pi)) * np.exp(-0.5 * z*z)

def runs_test(x, thr, alpha=0.05):
    x = np.asarray(x, dtype=float)
    b = (x >= thr).astype(int)
    n = len(b)
    n1 = int(b.sum())
    n2 = int(n - n1)

    R = 1 + int(np.sum(b[1:] != b[:-1]))
    muR = (2*n1*n2)/n + 1
    varR = (2*n1*n2*(2*n1*n2 - n)) / (n*n*(n-1))
    sigmaR = math.sqrt(varR) if varR > 0 else float("inf")
    z0 = (R - muR) / sigmaR

    zcrit = 1.959963984540054  # para alpha=0.05 (dos colas)
    pasa = abs(z0) <= zcrit

    return pasa, dict(n=n, thr=thr, n1=n1, n2=n2, R=R, muR=muR, sigmaR=sigmaR, z0=z0, zcrit=zcrit, alpha=alpha)

def plot_runs(info, title, out_png):
    z = np.linspace(-4, 4, 500)
    y = phi(z)

    plt.figure(figsize=(8.5, 4.8))
    plt.plot(z, y)
    plt.axvline(-info["zcrit"], linestyle="--")
    plt.axvline(+info["zcrit"], linestyle="--")
    plt.axvline(info["z0"])
    plt.title(title)
    plt.xlabel("z")
    plt.ylabel("densidad")

    txt = (
        f"alpha={info['alpha']:.2f}\n"
        f"n={info['n']}\n"
        f"thr={info['thr']}\n"
        f"n1={info['n1']}  n2={info['n2']}\n"
        f"R={info['R']}\n"
        f"z0={info['z0']:.4f}\n"
        f"zcrit=±{info['zcrit']:.4f}\n"
        f"{'No se rechaza H0' if abs(info['z0'])<=info['zcrit'] else 'Se rechaza H0'}"
    )
    plt.text(0.02, 0.95, txt, transform=plt.gca().transAxes, va="top")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

# --- Config de archivos (según tu Data/) ---
FILES = [
    # continuos [0,1): umbral 0.5
    ("java_u01.txt",   "continuous", (0, 1)),
    ("julia_u01.txt",  "continuous", (0, 1)),
    ("python_u01.txt", "continuous", (0, 1)),
    ("erlang_u01.txt", "continuous", (0, 1)),

    # discretos: umbral = media teórica (a+b)/2
    ("python_u1_6.txt","discrete",   (1, 6)),
    ("c_u1_4.txt",     "discrete",   (1, 4)),
    ("c_u1_8.txt",     "discrete",   (1, 8)),
    ("racket_u1_20.txt","discrete",  (1, 20)),
]

if __name__ == "__main__":
    for name, kind, (a,b) in FILES:
        f = DATA / name
        if not f.exists():
            continue

        x = np.loadtxt(f)
        thr = 0.5 if kind == "continuous" else (a + b) / 2.0

        pasa, info = runs_test(x, thr, alpha=0.05)

        out_png = OUT / f"{f.stem}_corridas.png"
        title = f"Prueba de Corridas (Z) — {f.name}"
        plot_runs(info, title, out_png)

        print(f"{f.name} | corridas PASA: {pasa} | z0={info['z0']:.4f} | zcrit=±{info['zcrit']:.4f}")
    print("Listo. Imágenes en:", OUT)