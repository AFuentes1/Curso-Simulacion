# src/Graficos/plot_series.py
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ALPHA = 0.05
K = 10  # 10x10 celdas


def series_test_and_plot(file_path: Path, out_png: Path, k: int = 10, alpha: float = 0.05):
    x = np.loadtxt(file_path, dtype=float)
    n = len(x)
    m = n - 1  # pares (u_i, u_{i+1})

    u = x[:-1]
    v = x[1:]

    # índices de celda 0..k-1 (por seguridad con valores 1.0)
    i = np.minimum((u * k).astype(int), k - 1)
    j = np.minimum((v * k).astype(int), k - 1)

    obs = np.zeros((k, k), dtype=int)
    np.add.at(obs, (i, j), 1)

    esperado = m / (k * k)
    chi0 = float(((obs - esperado) ** 2 / esperado).sum())
    df = k * k - 1

    # crítico (sin scipy): aproximación por normal para df grande
    # chi_crit ≈ df + z_(1-alpha)*sqrt(2*df)
    # para alpha=0.05 -> z=1.6448536269514722
    z = 1.6448536269514722
    chi_crit = float(df + z * np.sqrt(2 * df))

    pasa = chi0 < chi_crit

    # ---------- PLOT ----------
    fig = plt.figure(figsize=(10, 5))
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.imshow(obs, origin="lower", aspect="auto")
    ax1.set_title("Conteos (10x10)")
    ax1.set_xlabel("j")
    ax1.set_ylabel("i")

    ax2 = fig.add_subplot(1, 2, 2)
    # histograma de conteos por celda (para ver dispersión)
    ax2.hist(obs.ravel(), bins=20)
    ax2.set_title("Distribución de conteos")
    ax2.set_xlabel("conteo por celda")
    ax2.set_ylabel("frecuencia")

    titulo = f"Prueba de Series (χ²) — {file_path.name}"
    fig.suptitle(titulo, fontsize=14)

    txt = (
        f"alpha={alpha}\n"
        f"n={n}  m_pares={m}\n"
        f"k={k}  df={df}\n"
        f"esperado/celda={esperado:.2f}\n"
        f"chi0={chi0:.4f}\n"
        f"chi_crit≈{chi_crit:.4f}\n"
        f"{'No se rechaza H0' if pasa else 'Se rechaza H0'}"
    )
    fig.text(0.01, 0.02, txt, fontsize=10)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

    return pasa, {"n": n, "m_pares": m, "k": k, "alpha": alpha, "df": df, "chi0": chi0, "chi_crit": chi_crit}


def main():
    base_dir = Path(__file__).resolve().parents[2]  # .../Tarea 3
    sys.path.insert(0, str(base_dir))

    data_dir = base_dir / "Data"
    out_dir = base_dir / "results" / "Series"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = ["erlang_u01.txt", "java_u01.txt", "julia_u01.txt", "python_u01.txt"]

    for fname in files:
        fpath = data_dir / fname
        if not fpath.exists():
            print(f"{fname} | NO ENCONTRADO en {data_dir}")
            continue

        out_png = out_dir / fname.replace(".txt", "_series.png")
        pasa, info = series_test_and_plot(fpath, out_png, k=K, alpha=ALPHA)

        print(
            f"{fname} | PASA: {pasa} | "
            f"chi0={info['chi0']:.4f} crit≈{info['chi_crit']:.4f} df={info['df']} -> {out_png.name}"
        )

    print(f"\nListo. Imágenes en: {out_dir}")


if __name__ == "__main__":
    main()