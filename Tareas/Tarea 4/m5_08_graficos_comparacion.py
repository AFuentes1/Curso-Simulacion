import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom, betabinom, norm
from scipy.optimize import minimize

# ----------------- cargar datos -----------------
x = np.loadtxt("m5.txt", dtype=int)
n = len(x)

xmin, xmax = x.min(), x.max()          # 3..17
vals_x = np.arange(xmin, xmax + 1)

# FO / FR por valor
FO = np.array([(x == v).sum() for v in vals_x])
FR = FO / n

# Shift: Y = X-3 -> 0..14
y = x - xmin
N = xmax - xmin                         # 14
vals_y = np.arange(0, N + 1)

# ----------------- 1) Binomial desplazada -----------------
p_bin = y.mean() / N
pmf_bin = binom.pmf(vals_y, N, p_bin)

# ----------------- 2) Beta-Binomial MLE -----------------
def nll(theta):
    a = np.exp(theta[0])
    b = np.exp(theta[1])
    return -np.sum(betabinom.logpmf(y, N, a, b))

res = minimize(nll, x0=np.log([2.0, 2.0]), method="Nelder-Mead")
a_mle, b_mle = np.exp(res.x[0]), np.exp(res.x[1])
pmf_bb = betabinom.pmf(vals_y, N, a_mle, b_mle)

# ----------------- 3) Normal truncada/discretizada -----------------
mu = x.mean()
sigma = x.std()

a, b = xmin - 0.5, xmax + 0.5
mass = norm.cdf(b, mu, sigma) - norm.cdf(a, mu, sigma)

low = vals_x - 0.5
high = vals_x + 0.5
low[0] = a
high[-1] = b

pmf_normdisc = (norm.cdf(high, mu, sigma) - norm.cdf(low, mu, sigma)) / mass

# ----------------- GRAFICO 1: PMF (barras) + modelos -----------------
plt.figure()
plt.bar(vals_x, FR, width=0.9, align="center", label="Empírica (FR)")

plt.plot(vals_x, pmf_bin, marker="o", label=f"Binomial shift (N=14, p={p_bin:.4f})")
plt.plot(vals_x, pmf_bb, marker="o", label=f"Beta-Binomial MLE (a={a_mle:.3f}, b={b_mle:.3f})")
plt.plot(vals_x, pmf_normdisc, marker="o", label=f"Normal trunc/disc (mu={mu:.3f}, sigma={sigma:.3f})")

plt.title("m5: PMF empírica vs modelos")
plt.xlabel("x")
plt.ylabel("Probabilidad")
plt.legend()
plt.tight_layout()
plt.savefig("m5_pmf_comparacion.png", dpi=200)
plt.close()

# ----------------- GRAFICO 2: CDF empírica vs modelos -----------------
# CDF empírica en puntos enteros
F_emp = np.cumsum(FR)

F_bin = binom.cdf(vals_y, N, p_bin)
F_bb = betabinom.cdf(vals_y, N, a_mle, b_mle)
F_norm = np.cumsum(pmf_normdisc)

plt.figure()
plt.step(vals_x, F_emp, where="post", label="Empírica (CDF)")
plt.step(vals_x, F_bin, where="post", label="Binomial shift (CDF)")
plt.step(vals_x, F_bb, where="post", label="Beta-Binomial MLE (CDF)")
plt.step(vals_x, F_norm, where="post", label="Normal trunc/disc (CDF)")

plt.title("m5: CDF empírica vs modelos")
plt.xlabel("x")
plt.ylabel("F(x)")
plt.legend()
plt.tight_layout()
plt.savefig("m5_cdf_comparacion.png", dpi=200)
plt.close()

print("Listo. Se guardaron:")
print(" - m5_pmf_comparacion.png")
print(" - m5_cdf_comparacion.png")