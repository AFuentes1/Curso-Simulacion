# src/Graficos/plot_poker.py
from pathlib import Path
from collections import Counter

import numpy as np
import matplotlib.pyplot as plt


# Categorías (7)
CATS = [
    "Todos diferentes",
    "Un par",
    "Dos pares",
    "Tercia",
    "Full house",
    "Póker",
    "Quintilla",
]

def probs_poker_base10_5digits():
    # k = 10 símbolos (0..9), mano de 5
    k = 10
    den = k**5

    # Conteos combinatorios (ver diapositiva de probabilidades teóricas)
    all_diff   = k * 9 * 8 * 7 * 6
    one_pair   = k * (9*8*7//6) * (5*4*3*2*1 // 2)       # k * C(9,3) * 60
    two_pairs  = (k*(k-1)//2) * 8 * (5*4*3*2*1 // (2*2)) # C(10,2)*8*30
    three_kind = k * (9*8//2) * (5*4*3*2*1 // 6)         # k*C(9,2)*20
    full_house = k * 9 * (5*4*3*2*1 // (6*2))            # k*9*10
    four_kind  = k * 9 * 5
    five_kind  = k

    counts = np.array([all_diff, one_pair, two_pairs, three_kind, full_house, four_kind, five_kind], dtype=float)
    return counts / den


def hand_category_from_u(u: float, d: int = 5) -> int:
    # toma d dígitos decimales: u in [0,1)
    x = int(u * (10**d))  # 0..99999
    # extraer 5 "símbolos" base 10 (con ceros a la izquierda)
    digits = [(x // (10**i)) % 10 for i in range(d)]

    freq = sorted(Counter(digits).values(), reverse=True)  # ej: [2,1,1,1]
    if freq == [1,1,1,1,1]: return 0  # todos diferentes
    if freq == [2,1,1,1]:   return 1  # un par
    if freq == [2,2,1]:     return 2  # dos pares
    if freq == [3,1,1]:     return 3  # tercia
    if freq == [3,2]:       return 4  # full house
    if freq == [4,1]:       return 5  # póker
    if freq == [5]:         return 6  # quintilla
    return 0


def poker_test_and_plot(file_path: Path, alpha: float = 0.05, d: int = 5):
    u = np.loadtxt(file_path, dtype=float)
    n = len(u)

    probs = probs_poker_base10_5digits()
    exp = n * probs

    obs = np.zeros(7, dtype=float)
    for val in u:
        if 0.0 <= val < 1.0:
            obs[hand_category_from_u(val, d=d)] += 1

    chi0 = float(np.sum((obs - exp) ** 2 / exp))

    # Para df=6 y alpha=0.05, crítico ≈ 12.5916
    # (si tu profe usa otro alpha/df, ajustás aquí)
    crit = 12.5916
    pasa = chi0 <= crit

    # Plot (Observed vs Expected)
    x = np.arange(len(CATS))
    plt.figure(figsize=(10.5, 5.5))
    plt.bar(x, obs, alpha=0.85, label="Observado")
    plt.plot(x, exp, marker="o", linewidth=2, label="Esperado")
    plt.xticks(x, CATS, rotation=20, ha="right")
    plt.ylabel("Frecuencia")
    plt.title(f"Prueba de Póker (χ²) — {file_path.name}")
    plt.legend()
    plt.tight_layout()

    return pasa, chi0, crit


def main():
    base = Path(__file__).resolve().parents[2]          # .../Tarea 3
    data_dir = base / "Data"
    out_dir  = base / "results" / "Poker"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Poker SOLO para muestras U(0,1): archivos *_u01.txt
    for fp in sorted(data_dir.glob("*_u01.txt")):
        pasa, chi0, crit = poker_test_and_plot(fp, alpha=0.05, d=5)

        out_png = out_dir / f"{fp.stem}_poker.png"
        plt.savefig(out_png, dpi=200)
        plt.close()

        print(f"{fp.name} | PASA: {pasa} | chi0={chi0:.4f} crit={crit:.4f} -> {out_png.name}")


if __name__ == "__main__":
    main()