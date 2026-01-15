import numpy as np
from scipy.stats import norm, kstest

x = np.loadtxt("m5.txt", dtype=float)
n = len(x)

mu = x.mean()
sigma = x.std()

a, b = 2.5, 17.5
mass = norm.cdf(b, mu, sigma) - norm.cdf(a, mu, sigma)

def F_cond(z):
    return (norm.cdf(z, mu, sigma) - norm.cdf(a, mu, sigma)) / mass

# jitter para que K-S sea válido (continuo)
rng = np.random.default_rng(0)
xj = x + rng.uniform(-0.5, 0.5, size=n)

D, pval = kstest(xj, F_cond)
Dcrit = 1.36 / np.sqrt(n)

print("D =", D)
print("Dcrit =", Dcrit)
print("pval =", pval)