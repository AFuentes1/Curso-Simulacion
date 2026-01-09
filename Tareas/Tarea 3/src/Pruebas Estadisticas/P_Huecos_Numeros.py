import numpy as np
from scipy.stats import chi2
from pathlib import Path

def contar_huecos(u, u0=0.0, u1=0.5):
    # Huecos entre "hits" u in [u0, u1)
    hit = (u >= u0) & (u < u1)

    gaps = []
    gap = 0
    started = False  # empieza a contar después del primer hit

    for h in hit:
        if h:
            if started:
                gaps.append(gap)
            started = True
            gap = 0
        else:
            if started:
                gap += 1

    return gaps

def prueba_huecos_numeros(path, a=0, b=1, u0=0.0, u1=0.5, alpha=0.05, kmax=5):
    x = np.loadtxt(path)
    n = x.size

    # Normalizar a U(0,1) si tus datos son U(a,b)
    u = (x - a) / (b - a)

    gaps = contar_huecos(u, u0=u0, u1=u1)
    m = len(gaps)  # cantidad de huecos observados (entre hits)

    if m < 5:
        return False, {
            "error": "Muy pocos huecos (pocos hits). Use más datos o cambie el intervalo [u0,u1).",
            "n": int(n),
            "m_huecos": int(m)
        }

    p = (u1 - u0)
    q = 1 - p

    # Observados: clases 0..kmax y >=kmax+1
    obs = [0] * (kmax + 2)
    for g in gaps:
        if g <= kmax:
            obs[g] += 1
        else:
            obs[kmax + 1] += 1

    # Esperados según geométrica
    exp = []
    for k in range(0, kmax + 1):
        exp.append(m * (q**k) * p)
    exp.append(m * (q**(kmax + 1)))  # cola: P(G >= kmax+1)

    # Chi-cuadrado (bondad de ajuste)
    chi0 = 0.0
    for O, E in zip(obs, exp):
        if E > 0:
            chi0 += (O - E) ** 2 / E

    df = (kmax + 2) - 1  # #clases - 1
    chi_crit = chi2.ppf(1 - alpha, df)
    pasa = (chi0 <= chi_crit)

    return pasa, {
        "n": int(n),
        "m_huecos": int(m),
        "intervalo": [float(u0), float(u1)],
        "p": float(p),
        "kmax": int(kmax),
        "obs": obs,   # [0,1,2,...,kmax, >=kmax+1]
        "exp": [float(e) for e in exp],
        "alpha": float(alpha),
        "chi0": float(chi0),
        "chi_crit": float(chi_crit),
        "df": int(df)
    }

# --- Ejecutar con el botón ▶ ---
data_path = Path(__file__).resolve().parents[2] / "Data" / "python_u01.txt"

pasa, info = prueba_huecos_numeros(str(data_path), a=0, b=1, u0=0.0, u1=0.5, alpha=0.05, kmax=5)
print("HUECOS (NÚMEROS) PASA:", pasa)
print(info)
