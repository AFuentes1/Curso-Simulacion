import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2
from pathlib import Path

ALPHA = 0.05
HITS  = {0,1,2,3,4}   # “hits” = dígitos 0..4
KMAX  = 5             # clases 0..5 y cola >=6

def primer_digito_decimal(x):
    return (np.floor((x + 1e-12) * 10).astype(int) % 10)

def gaps_por_hits(d, hits=HITS, kmax=KMAX):
    hit = np.isin(d, list(hits))
    gaps, gap, started = [], 0, False
    for h in hit:
        if h:
            if started: gaps.append(gap)
            started, gap = True, 0
        elif started:
            gap += 1

    m = len(gaps)
    p = len(hits)/10.0
    q = 1 - p

    obs = [0]*(kmax+2)               # 0..kmax y cola
    for g in gaps:
        obs[g if g <= kmax else kmax+1] += 1

    exp = [m*(q**k)*p for k in range(kmax+1)]
    exp.append(m*(q**(kmax+1)))      # cola

    chi0 = sum((O-E)**2/E for O,E in zip(obs,exp) if E > 0)
    df = (kmax+2) - 1
    return m, p, obs, exp, chi0, df

def plot_huecos_digitos(file_path: Path, out_dir: Path):
    x = np.loadtxt(file_path)
    x = x[(x >= 0) & (x < 1)]
    d = primer_digito_decimal(x)

    m, p, obs, exp, chi0, df = gaps_por_hits(d)
    crit = chi2.ppf(1-ALPHA, df)
    pasa = chi0 <= crit

    # --- figura (resumen + barras obs/esp) ---
    plt.figure(figsize=(11, 5))
    gs = plt.GridSpec(1, 2, width_ratios=[1, 1.6])

    ax0 = plt.subplot(gs[0])
    ax0.axis("off")
    txt = (
        f"α = {ALPHA}\n"
        f"n = {len(d):,}\n"
        f"hits = {sorted(HITS)}  (p={p:.1f})\n"
        f"kmax = {KMAX}\n"
        f"m (huecos) = {m:,}\n"
        f"df = {df}\n"
        f"χ²0 = {chi0:.4f}\n"
        f"χ²crit = {crit:.4f}\n\n"
        f"Decisión: {'No se rechaza H0' if pasa else 'Se rechaza H0'}"
    )
    ax0.text(0.02, 0.98, txt, va="top", fontsize=14)

    ax1 = plt.subplot(gs[1])
    labels = [str(k) for k in range(KMAX+1)] + [f"≥{KMAX+1}"]
    idx = np.arange(len(labels))
    ax1.bar(idx - 0.2, obs, width=0.4, label="Observado")
    ax1.bar(idx + 0.2, exp, width=0.4, label="Esperado")
    ax1.set_xticks(idx)
    ax1.set_xticklabels(labels)
    ax1.set_xlabel("Longitud del hueco")
    ax1.set_ylabel("Frecuencia")
    ax1.set_title(f"Huecos con dígitos — {file_path.name}")
    ax1.legend()

    plt.tight_layout()
    out = out_dir / f"{file_path.stem}_huecos_digitos.png"
    plt.savefig(out, dpi=200)
    plt.close()

    print(f"{file_path.name} | PASA: {pasa} | chi0={chi0:.4f} crit={crit:.4f} -> {out.name}")

if __name__ == "__main__":
    BASE = Path(__file__).resolve().parents[2]   # .../Tarea 3
    DATA = BASE / "Data"
    NORM = DATA / "_norm"
    OUT  = BASE / "results"
    OUT.mkdir(exist_ok=True)

    files = [
        DATA/"java_u01.txt", DATA/"julia_u01.txt", DATA/"python_u01.txt", DATA/"erlang_u01.txt",
        NORM/"c_u1_4_u01.txt", NORM/"c_u1_8_u01.txt", NORM/"python_u1_6_u01.txt", NORM/"racket_u1_20_u01.txt",
    ]

    for f in files:
        if f.exists():
            plot_huecos_digitos(f, OUT)