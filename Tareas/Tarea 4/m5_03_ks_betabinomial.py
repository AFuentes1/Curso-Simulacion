import numpy as np
from scipy.stats import betabinom

x = np.loadtxt("m5.txt", dtype=int)
x_sorted = np.sort(x)
n = len(x_sorted)

nn = 14
a, b = 3.60, 4.15

F = betabinom.cdf(x_sorted - 3, nn, a, b)
Fn = np.arange(1, n + 1) / n

D = np.max(np.abs(Fn - F))
Dcrit = 1.36 / np.sqrt(n)

print("D =", D)
print("Dcrit =", Dcrit)