import numpy as np
from scipy.stats import betabinom, chi2

x = np.loadtxt("m5.txt", dtype=int)
n = len(x)
vals = np.arange(3, 18)
FO = np.array([(x == v).sum() for v in vals])

nn = 14
a, b = 3.60, 4.15
y = vals - 3

pi = betabinom.pmf(y, nn, a, b)
FE = n * pi

chi2_stat = ((FO - FE)**2 / FE).sum()
df = len(vals) - 1 - 2
pval = 1 - chi2.cdf(chi2_stat, df)

print("chi2 =", chi2_stat)
print("df =", df)
print("pval =", pval)