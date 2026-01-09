import numpy as np
from scipy.stats import norm
from pathlib import Path

def contar_corridas(bits):
    # bits: lista/array de 0 y 1
    if len(bits) == 0:
        return 0
    r = 1
    for i in range(1, len(bits)):
        if bits[i] != bits[i-1]:
            r += 1
    return r

def prueba_corridas(path, alpha=0.05):
    x = np.loadtxt(path)
    n = x.size
    threshold = len(set(x)) / 2  # mediana aproximada
    # 1 si está arriba/igual al umbral, 0 si está abajo
    bits = (x >= threshold).astype(int)

    n1 = int(bits.sum())      # cantidad de "arriba"
    n0 = int(n - n1)          # cantidad de "abajo"

    # Si todo cayó de un solo lado, no tiene sentido la prueba
    if n0 == 0 or n1 == 0:
        return False, {
            "n": int(n),
            "n0": int(n0),
            "n1": int(n1),
            "error": "Todos los valores quedaron del mismo lado del umbral."
        }

    R = contar_corridas(bits)

    muR = (2 * n0 * n1) / n + 1
    varR = (2 * n0 * n1 * (2 * n0 * n1 - n)) / (n**2 * (n - 1))
    sigmaR = np.sqrt(varR)

    z0 = (R - muR) / sigmaR
    zcrit = norm.ppf(1 - alpha/2)

    pasa = (-zcrit <= z0 <= zcrit)

    return pasa, {
        "n": int(n),
        "threshold": float(threshold),
        "n0": int(n0),
        "n1": int(n1),
        "R_corridas": int(R),
        "muR": float(muR),
        "sigmaR": float(sigmaR),
        "alpha": float(alpha),
        "z0": float(z0),
        "zona_aceptacion_z": [float(-zcrit), float(zcrit)]
    }

if __name__ == "__main__":
    # Ruta robusta (si tu .py está en .../Tarea 3/src/ y data en .../Tarea 3/data/)
    data_path = Path(__file__).resolve().parents[2] / "Data" / "python_u01.txt"

    pasa, info = prueba_corridas(data_path, alpha=0.05)
    print("CORRIDAS PASA:", pasa)
    print(info)
