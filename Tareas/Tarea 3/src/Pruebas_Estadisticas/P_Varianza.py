import numpy as np
from scipy.stats import norm, chi2
from pathlib import Path

def params_uniform(kind, a, b):
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
    x = np.loadtxt(path)
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
        "sigma2_teorica": float(sigma2),
        "alpha": float(alpha),
        "intervalo": [float(low), float(high)]
    }

def prueba_varianza(path, kind="continuous", a=0, b=1, alpha=0.05):
    x = np.loadtxt(path)
    n = x.size

    _, sigma2_teo = params_uniform(kind, a, b)

    # s^2 muestral con n-1 (IMPORTANTE para chi-cuadrado)
    s2 = x.var(ddof=1)

    df = n - 1
    chi0 = df * s2 / sigma2_teo

    chi_low = chi2.ppf(alpha/2, df)
    chi_high = chi2.ppf(1 - alpha/2, df)

    pasa = (chi_low <= chi0 <= chi_high)

    return pasa, {
        "n": int(n),
        "s2_muestral": float(s2),
        "sigma2_teorica": float(sigma2_teo),
        "df": int(df),
        "alpha": float(alpha),
        "chi0": float(chi0),
        "zona_aceptacion": [float(chi_low), float(chi_high)]
    }

# --- RUTA ROBUSTA (sin main) ---
data_path = Path(__file__).resolve().parents[2] / "Data" / "python_u01.txt"

pasa_var, info_var = prueba_varianza(data_path, kind="continuous", a=0, b=1, alpha=0.05)
print("\nVARIANZA PASA:", pasa_var)
print(info_var)
