import numpy as np
from scipy.stats import chi2
from pathlib import Path

def primer_digito_decimal(x):
    return (np.floor((x + 1e-12) * 10).astype(int) % 10)

def chi_cuadrado_digitos(d):
    n = len(d)
    obs = np.bincount(d, minlength=10)
    exp = np.full(10, n / 10.0)
    chi0 = np.sum((obs - exp) ** 2 / exp)
    df = 9
    return chi0, df, obs

def huecos_digitos(d, hits={0,1,2,3,4}, kmax=5):
    hit = np.isin(d, list(hits))
    gaps, gap, started = [], 0, False

    for h in hit:
        if h:
            if started:
                gaps.append(gap)
            started = True
            gap = 0
        else:
            if started:
                gap += 1

    m = len(gaps)
    p = len(hits) / 10.0
    q = 1 - p

    obs = [0] * (kmax + 2)  # 0..kmax y cola
    for g in gaps:
        if g <= kmax:
            obs[g] += 1
        else:
            obs[kmax + 1] += 1

    exp = [m * (q**k) * p for k in range(0, kmax + 1)]
    exp.append(m * (q**(kmax + 1)))

    chi0 = sum((O - E) ** 2 / E for O, E in zip(obs, exp) if E > 0)
    df = (kmax + 2) - 1
    return chi0, df, obs, exp, m

# --- Ejecutar con el botón ▶ ---
if __name__ == "__main__":
    data_path = Path(__file__).resolve().parents[2] / "Data" / "python_u01.txt"

    x = np.loadtxt(data_path)
    x = x[(x >= 0) & (x < 1)]
    d = primer_digito_decimal(x)

    alpha = 0.05

    chi0, df, obs = chi_cuadrado_digitos(d)
    crit = chi2.ppf(1 - alpha, df)
    print("DIGITOS PASA:", chi0 <= crit)
    print({"chi0": float(chi0), "chi_crit": float(crit), "df": int(df), "obs": obs.tolist()})

    chi0g, dfg, obs_g, exp_g, m = huecos_digitos(d, hits={0,1,2,3,4}, kmax=5)
    critg = chi2.ppf(1 - alpha, dfg)
    print("\nHUECOS(DIGITOS) PASA:", chi0g <= critg)
    print({"m": int(m), "chi0": float(chi0g), "chi_crit": float(critg), "df": int(dfg), "obs": obs_g, "exp": [float(e) for e in exp_g]})