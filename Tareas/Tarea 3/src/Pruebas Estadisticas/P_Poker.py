import numpy as np
from scipy.stats import chi2
from pathlib import Path
from collections import Counter

def poker_categoria_5dig(digitos):
    # digitos: lista de 5 enteros (0..9)
    c = Counter(digitos)
    patron = sorted(c.values(), reverse=True)  # ej: [2,1,1,1]
    if patron == [1,1,1,1,1]: return "todos_dif"
    if patron == [2,1,1,1]:   return "un_par"
    if patron == [2,2,1]:     return "dos_pares"
    if patron == [3,1,1]:     return "trio"
    if patron == [3,2]:       return "full"
    if patron == [4,1]:       return "poker"
    if patron == [5]:         return "quintilla"
    return "otro"  # por si acaso

def prueba_poker(path, a=0, b=1, alpha=0.05, d=5):
    x = np.loadtxt(path)
    n = x.size

    # Normalizar a U(0,1) si venís de U(a,b)
    u = (x - a) / (b - a)

    # Convertir cada u en un entero 0..10^d-1 y sacar sus d dígitos
    base = 10**d
    ints = (u * base).astype(int)
    ints = np.clip(ints, 0, base - 1)

    # Contar categorías observadas
    obs = {
        "todos_dif": 0,
        "un_par": 0,
        "dos_pares": 0,
        "trio": 0,
        "full": 0,
        "poker": 0,
        "quintilla": 0
    }

    for val in ints:
        s = str(val).zfill(d)                 # ej: "00473"
        dig = [int(ch) for ch in s]           # [0,0,4,7,3]
        cat = poker_categoria_5dig(dig)
        obs[cat] += 1

    # Probabilidades teóricas para d=5 (base 10)
    probs = {
        "todos_dif": 0.30240,
        "un_par":    0.50400,
        "dos_pares": 0.10800,
        "trio":      0.07200,
        "full":      0.00900,
        "poker":     0.00450,
        "quintilla": 0.00010
    }

    # Armar listas en orden (de más común a más raro)
    orden = ["todos_dif","un_par","dos_pares","trio","full","poker","quintilla"]
    O = [obs[k] for k in orden]
    E = [n * probs[k] for k in orden]

    # (Opcional pero correcto) si alguna esperada < 5, se combinan colas raras
    # Combina desde el final hacia atrás hasta que todas las E sean >= 5
    while len(E) > 2 and min(E) < 5:
        E[-2] += E[-1]
        O[-2] += O[-1]
        E.pop(); O.pop()
        orden.pop()

    chi0 = sum((o - e)**2 / e for o, e in zip(O, E))
    df = len(O) - 1
    chi_crit = chi2.ppf(1 - alpha, df)
    pasa = (chi0 <= chi_crit)

    return pasa, {
        "n": int(n),
        "alpha": float(alpha),
        "categorias": orden,
        "obs": O,
        "esp": [float(e) for e in E],
        "chi0": float(chi0),
        "chi_crit": float(chi_crit),
        "df": int(df)
    }

# --- Ejecutar con el botón ▶ ---
data_path = Path(__file__).resolve().parents[2] / "Data" / "python_u01.txt"

pasa, info = prueba_poker(str(data_path), a=0, b=1, alpha=0.05, d=5)
print("POKER PASA:", pasa)
print(info)
