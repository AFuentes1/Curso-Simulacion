import numpy as np
from collections import Counter

x = np.loadtxt("m5.txt", dtype=int)

n = len(x)
print("n =", n)
print("min =", x.min(), "max =", x.max())
print("media =", x.mean())
print("var =", x.var())
print("desv =", x.std())

c = Counter(x)
vals = range(x.min(), x.max()+1)
FO = np.array([c[v] for v in vals])
FR = FO / n

for v, fo, fr in zip(vals, FO, FR):
    print(v, fo, fr)