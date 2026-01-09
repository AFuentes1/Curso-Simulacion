import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "Data"
OUT  = Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)

def plot_continuous(file, bins=50):
    x = np.loadtxt(file)
    plt.figure()
    plt.hist(x, bins=bins)
    plt.title(file.name)
    plt.xlabel("valor")
    plt.ylabel("frecuencia")
    plt.tight_layout()
    plt.savefig(OUT / f"{file.stem}_hist.png", dpi=200)
    plt.close()

def plot_discrete(file):
    x = np.loadtxt(file, dtype=int)
    vals, counts = np.unique(x, return_counts=True)
    plt.figure()
    plt.bar(vals, counts)
    plt.title(file.name)
    plt.xlabel("valor")
    plt.ylabel("frecuencia")
    plt.tight_layout()
    plt.savefig(OUT / f"{file.stem}_bars.png", dpi=200)
    plt.close()

if __name__ == "__main__":
    # Continuos [0,1)
    for name in ["java_u01.txt","julia_u01.txt","python_u01.txt","python_u02.txt"]:
        f = DATA / name
        if f.exists():
            plot_continuous(f, bins=50)

    # Discretos
    for name in ["c_u01.txt","c_u02.txt","racket_1_20.txt"]:
        f = DATA / name
        if f.exists():
            plot_discrete(f)

    print("Listo. Imágenes en:", OUT)