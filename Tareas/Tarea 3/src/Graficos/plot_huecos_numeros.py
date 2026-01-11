# src/Graficos/plot_huecos_numeros.py
from pathlib import Path
import math

import matplotlib.pyplot as plt

try:
    from scipy.stats import chi2
except Exception as e:
    raise SystemExit("Falta scipy. Instale con: pip3 install scipy") from e


def iter_numbers(txt_path: Path):
    with txt_path.open("r") as f:
        for line in f:
            s = line.strip()
            if s:
                yield float(s)


def huecos_numeros_test(file_path: Path, u0=0.0, u1=0.5, kmax=5, alpha=0.05):
    # p = prob. de "hit" (caer en [u0,u1))
    p = max(0.0, min(1.0, u1 - u0))
    q = 1.0 - p

    obs = [0] * (kmax + 1)  # 0..kmax-1 y ">=kmax"
    n_hits = 0
    gaps_counted = 0

    gap = None  # None = aún no hemos visto el primer "hit"

    for x in iter_numbers(file_path):
        hit = (u0 <= x < u1)
        if hit:
            n_hits += 1
            if gap is not None:
                idx = gap if gap < kmax else kmax
                obs[idx] += 1
                gaps_counted += 1
            gap = 0
        else:
            if gap is not None:
                gap += 1

    # Si hay <2 hits, no se puede contar huecos entre hits
    if gaps_counted == 0:
        return False, {
            "error": "No hay suficientes hits para formar huecos (se requieren >= 2 hits).",
            "n_hits": n_hits
        }

    # Esperados (geométrica en cantidad de fallos antes del próximo hit)
    probs = [(q ** k) * p for k in range(kmax)]
    probs.append(q ** kmax)  # >=kmax

    exp = [gaps_counted * pr for pr in probs]

    # chi^2
    chi0 = 0.0
    for o, e in zip(obs, exp):
        if e > 0:
            chi0 += (o - e) ** 2 / e

    df = kmax  # (kmax+1 categorías) - 1
    crit = float(chi2.ppf(1 - alpha, df))
    pasa = chi0 < crit

    return pasa, {
        "alpha": alpha,
        "u0": u0, "u1": u1, "kmax": kmax,
        "df": df,
        "n_hits": n_hits,
        "gaps": gaps_counted,
        "obs": obs,
        "exp": exp,
        "chi0": chi0,
        "crit": crit,
    }


def plot_obs_exp(info, title, out_path: Path):
    obs = info["obs"]
    exp = info["exp"]
    kmax = info["kmax"]

    labels = [str(k) for k in range(kmax)] + [f"$\\geq{ kmax }$"]
    x = list(range(len(labels)))

    plt.figure(figsize=(10, 4.6))
    plt.title(title)
    plt.bar(x, obs, alpha=0.9, label="Observado")
    plt.plot(x, exp, marker="o", linewidth=2, label="Esperado")
    plt.xticks(x, labels)
    plt.xlabel("Longitud del hueco (fallos antes del hit)")
    plt.ylabel("Frecuencia")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main():
    ROOT = Path(__file__).resolve().parents[2]   # .../Tarea 3
    DATA = ROOT / "Data"
    OUTDIR = ROOT / "results" / "Huecos_Numeros"
    OUTDIR.mkdir(parents=True, exist_ok=True)

    alpha = 0.05
    u0, u1 = 0.0, 0.5
    kmax = 5

    # SOLO continuas: *_u01.txt (java_u01, julia_u01, python_u01, erlang_u01)
    files = []
    for p in sorted(DATA.glob("*.txt")):
        stem = p.stem
        parts = stem.split("_")
        if len(parts) == 2 and parts[1] == "u01":
            files.append(p)

    if not files:
        print(f"No encontré archivos *_u01.txt en: {DATA}")
        return

    for fp in files:
        pasa, info = huecos_numeros_test(fp, u0=u0, u1=u1, kmax=kmax, alpha=alpha)
        if "error" in info:
            print(f"{fp.name} | ERROR: {info['error']}")
            continue

        out_png = OUTDIR / f"{fp.stem}_huecos_numeros.png"
        plot_obs_exp(info, f"Huecos con Números (χ²) — {fp.name}", out_png)

        print(
            f"{fp.name} | PASA: {pasa} | "
            f"chi0={info['chi0']:.4f} crit={info['crit']:.4f} -> {out_png.name}"
        )

    print(f"Listo. Imágenes en: {OUTDIR}")


if __name__ == "__main__":
    main()