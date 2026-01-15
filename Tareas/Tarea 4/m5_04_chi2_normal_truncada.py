import numpy as np
from scipy.stats import norm, chi2

x = np.loadtxt("m5.txt", dtype=float)
n = len(x)

mu = x.mean()
sigma = x.std()

# Normal condicionada a [2.5, 17.5] para modelar discretización 3..17
a, b = 2.5, 17.5
mass = norm.cdf(b, mu, sigma) - norm.cdf(a, mu, sigma)

vals = np.arange(3, 18)
FO = np.array([(x == v).sum() for v in vals])

low = vals - 0.5
high = vals + 0.5
low[0] = a
high[-1] = b

pi = (norm.cdf(high, mu, sigma) - norm.cdf(low, mu, sigma)) / mass
FE = n * pi

chi2_stat = ((FO - FE) ** 2 / FE).sum()
df = len(vals) - 1 - 2  # k-1-m (m=2: mu y sigma)
pval = 1 - chi2.cdf(chi2_stat, df)

print("chi2 =", chi2_stat)
print("df =", df)
print("pval =", pval)