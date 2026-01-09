import numpy as np
from scipy.stats import norm
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
        "sigma2": float(sigma2),
        "alpha": float(alpha),
        "intervalo": [float(low), float(high)]
    }


data_path = Path(__file__).resolve().parents[2] / "Data" / "python_u01.txt"

pasa, info = prueba_promedio(data_path, kind="continuous", a=0, b=1, alpha=0.05)
print("PROMEDIO PASA:", pasa)
print(info)
