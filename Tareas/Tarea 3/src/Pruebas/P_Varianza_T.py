import numpy as np
from scipy.stats import chi2
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "Data"
ALPHA = 0.05

# nombre_archivo : (tipo, parametro)
# tipo="cont01" => var=1/12 ; tipo="disc1m" => var=(m^2-1)/12
FILES = {
    "java_u01.txt":   ("cont01", None),
    "julia_u01.txt":  ("cont01", None),
    "python_u01.txt": ("cont01", None),
    "erlang_u01.txt": ("cont01", None),

    "python_u1_6.txt": ("disc1m", 6),
    "c_u1_4.txt":      ("disc1m", 4),
    "c_u1_8.txt":      ("disc1m", 8),
    "racket_u1_20.txt":("disc1m", 20),
}

def sigma2_teorica(tipo, m):
    if tipo == "cont01":  return 1/12
    if tipo == "disc1m":  return (m*m - 1)/12
    raise ValueError("tipo desconocido")

def test_varianza(file_path, tipo, m=None, alpha=0.05):
    x = np.loadtxt(file_path)
    n = len(x)
    df = n - 1
    s2 = np.var(x, ddof=1)
    sig2 = sigma2_teorica(tipo, m)

    chi0 = df * s2 / sig2
    low = chi2.ppf(alpha/2, df)
    high = chi2.ppf(1 - alpha/2, df)
    pasa = (low <= chi0 <= high)

    return pasa, {"n": n, "s2": s2, "sigma2": sig2, "df": df, "chi0": chi0, "low": low, "high": high}

if __name__ == "__main__":
    for name, (tipo, m) in FILES.items():
        f = DATA / name
        if not f.exists():
            print(f"{name}: NO EXISTE")
            continue
        pasa, info = test_varianza(f, tipo, m, ALPHA)
        print(f"\n{name} | PASA: {pasa}")
        print(info)