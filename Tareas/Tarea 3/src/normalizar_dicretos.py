import numpy as np
from pathlib import Path

from pathlib import Path

BASE = Path(__file__).resolve().parents[1]   # .../Tarea 3
DATA = BASE / "Data"
NORM = DATA / "_norm"
NORM.mkdir(parents=True, exist_ok=True)

# k = tamaño del conjunto {1..k}
DISCRETOS = {
    "python_u1_6.txt": 6,
    "c_u1_4.txt": 4,
    "c_u1_8.txt": 8,
    "racket_u1_20.txt": 20,
}

for fname, k in DISCRETOS.items():
    src = DATA / fname
    x = np.loadtxt(src)          # enteros
    u = (x - 1.0) / k            # -> [0,1)
    dst = NORM / f"{src.stem}_u01.txt"
    np.savetxt(dst, u, fmt="%.16f")
    print("OK:", dst)