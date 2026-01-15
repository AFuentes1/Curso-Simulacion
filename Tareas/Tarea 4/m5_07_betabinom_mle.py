import numpy as np
from scipy.stats import betabinom, chi2, kstest
from scipy.optimize import minimize

x = np.loadtxt("m5.txt", dtype=int)
n = len(x)

# Y = X - 3  -> soporte 0..14
y = x - 3
N = 14

# ---------- MLE para alpha, beta ----------
def nll(theta):
    # theta = (log_alpha, log_beta) para asegurar positivos
    a = np.exp(theta[0])
    b = np.exp(theta[1])
    return -np.sum(betabinom.logpmf(y, N, a, b))

res = minimize(nll, x0=np.log([2.0, 2.0]), method="Nelder-Mead")
a_mle, b_mle = np.exp(res.x[0]), np.exp(res.x[1])

print("BETABINOM MLE")
print("N =", N, "alpha =", a_mle, "beta =", b_mle)

# ---------- Chi-cuadrado ----------
vals = np.arange(0, N+1)
FO = np.array([(y == v).sum() for v in vals])

pi = betabinom.pmf(vals, N, a_mle, b_mle)
FE = n * pi

chi2_stat = ((FO - FE)**2 / FE).sum()
df = len(vals) - 1 - 2  # k-1-m (m=2: alpha,beta)
pval_chi2 = 1 - chi2.cdf(chi2_stat, df)

print("chi2 =", chi2_stat)
print("df =", df)
print("pval =", pval_chi2)

# ---------- K-S (con jitter) ----------
rng = np.random.default_rng(0)
yj = y + rng.uniform(-0.5, 0.5, size=n)

def F(z):
    return betabinom.cdf(np.floor(z + 0.5), N, a_mle, b_mle)

D, pval_ks = kstest(yj, F)
Dcrit = 1.36 / np.sqrt(n)

print("D =", D)
print("Dcrit =", Dcrit)
print("pval_ks =", pval_ks)