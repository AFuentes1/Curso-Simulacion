import numpy as np
from scipy.stats import chi2
from pathlib import Path

def prueba_series(path, a=0, b=1, k=10, alpha=0.05):
    x = np.loadtxt(path)
    n = x.size
    if n < 2:
        return False, {"error": "Se requieren al menos 2 datos."}

    # Normalizar a U(0,1) si venís de U(a,b)
    u = (x - a) / (b - a)

    # Pares consecutivos (solapados): (u0,u1), (u1,u2), ..., (u[n-2],u[n-1])
    u1 = u[:-1]
    u2 = u[1:]
    m = u1.size  # cantidad de pares

    # Índice de celda para cada componente (0..k-1)
    i = np.floor(u1 * k).astype(int)
    j = np.floor(u2 * k).astype(int)

    # Por seguridad (si cae exactamente en 1.0 por redondeos)
    i = np.clip(i, 0, k - 1)
    j = np.clip(j, 0, k - 1)

    # Contar frecuencias en la grilla kxk
    tabla = np.zeros((k, k), dtype=int)
    for r, c in zip(i, j):
        tabla[r, c] += 1

    # Esperado por celda
    E = m / (k * k)

    # Regla práctica: E debería ser >= 5 para chi-cuadrado
    if E < 5:
        return False, {
            "error": "Esperado por celda < 5. Use un k más pequeño o más datos.",
            "n": int(n),
            "m_pares": int(m),
            "k": int(k),
            "esperado_por_celda": float(E)
        }

    # Chi-cuadrado
    chi0 = np.sum((tabla - E) ** 2 / E)
    df = k * k - 1
    chi_crit = chi2.ppf(1 - alpha, df)

    pasa = (chi0 <= chi_crit)

    return pasa, {
        "n": int(n),
        "m_pares": int(m),
        "k": int(k),
        "alpha": float(alpha),
        "esperado_por_celda": float(E),
        "chi0": float(chi0),
        "chi_crit": float(chi_crit),
        "df": int(df)
        # si querés ver la tabla completa, te la imprimo aparte
    }

# --- Ejecutar con el botón ▶ ---
data_path = Path(__file__).resolve().parents[2] / "Data" / "python_u01.txt"

pasa, info = prueba_series(data_path, a=0, b=1, k=10, alpha=0.05)
print("SERIES PASA:", pasa)
print(info)
