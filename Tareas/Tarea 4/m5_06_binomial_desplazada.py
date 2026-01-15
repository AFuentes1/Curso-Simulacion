import numpy as np
from scipy.stats import binom, chi2, kstest

x = np.loadtxt("m5.txt", dtype=int)
n = len(x)

# Shift: Y = X - 3  -> soporte 0..14
y = x - 3
N = 14

# p por momentos: E[Y]=Np  => p = mean(y)/N
p = y.mean() / N

# ---------- Chi-cuadrado ----------
vals = np.arange(0, N+1)
FO = np.array([(y == v).sum() for v in vals])

pi = binom.pmf(vals, N, p)
FE = n * pi

chi2_stat = ((FO - FE)**2 / FE).sum()
df = len(vals) - 1 - 1  # k-1-m (m=1 parámetro: p)
pval_chi2 = 1 - chi2.cdf(chi2_stat, df)

print("BINOMIAL SHIFT")
print("N =", N, "p =", p)
print("chi2 =", chi2_stat)
print("df =", df)
print("pval =", pval_chi2)

# ---------- K-S (con jitter para continuo) ----------
rng = np.random.default_rng(0)
yj = y + rng.uniform(-0.5, 0.5, size=n)

def F(z):
    return binom.cdf(np.floor(z + 0.5), N, p)

D, pval_ks = kstest(yj, F)
Dcrit = 1.36 / np.sqrt(n)

print("D =", D)
print("Dcrit =", Dcrit)
print("pval_ks =", pval_ks)