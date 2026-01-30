# ===============================
# tests_distributions.py
# ===============================
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import numpy as np
from scipy import stats


# ===============================
# DistSpec (igual al del modelo)
# ===============================
@dataclass
class DistSpec:
    name: str
    shape: tuple = ()
    loc: float = 0.0
    scale: float = 1.0


# ===============================
# Distribución -> scipy rv
# ===============================
def get_rv(spec: DistSpec):
    if not hasattr(stats, spec.name):
        raise ValueError(f"Distribución '{spec.name}' no existe en scipy.stats")
    dist = getattr(stats, spec.name)
    return dist(*spec.shape, loc=spec.loc, scale=spec.scale)


# ===============================
# Generadores de muestras
# ===============================
def sample_continuous(
    spec: DistSpec,
    n: int,
    seed: int | None = None
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    rv = get_rv(spec)
    samples = rv.rvs(size=n, random_state=rng)
    return np.maximum(samples, 0.0)


def sample_binomial(
    n_samples: int,
    n: int,
    p: float,
    seed: int | None = None
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.binomial(n, p, size=n_samples)


# ===============================
# Tests estadísticos
# ===============================
def ks_test(samples: np.ndarray, spec: DistSpec) -> Tuple[float, float]:
    rv = get_rv(spec)
    stat, p_value = stats.kstest(samples, rv.cdf)
    return stat, p_value


def chi_square_binomial(
    samples: np.ndarray,
    n: int,
    p: float
) -> Tuple[float, float]:
    values, observed = np.unique(samples, return_counts=True)
    expected = stats.binom.pmf(values, n, p) * len(samples)
    stat, p_value = stats.chisquare(observed, expected)
    return stat, p_value


# ===============================
# Ejemplo de uso
# ===============================
if __name__ == "__main__":

    N = 20_000
    SEED = 123

    # --- Exponencial (ej: llegadas o cajas)
    exp_spec = DistSpec(
        name="expon",
        loc=0.0,
        scale=2.5   # media
    )

    samples_exp = sample_continuous(exp_spec, N, SEED)
    ks_stat, ks_p = ks_test(samples_exp, exp_spec)

    print("KS Exponencial")
    print("  estadístico:", ks_stat)
    print("  p-value    :", ks_p)
    print()

    # --- Normal discreta (freidora antes de discretizar)
    norm_spec = DistSpec(
        name="norm",
        loc=3.0,
        scale=1.0
    )

    samples_norm = sample_continuous(norm_spec, N, SEED)
    ks_stat, ks_p = ks_test(samples_norm, norm_spec)

    print("KS Normal")
    print("  estadístico:", ks_stat)
    print("  p-value    :", ks_p)
    print()

    # --- Binomial (cantidad de órdenes)
    samples_bin = sample_binomial(N, n=5, p=2/5, seed=SEED)
    chi_stat, chi_p = chi_square_binomial(samples_bin, n=5, p=2/5)

    print("Ji-cuadrado Binomial")
    print("  estadístico:", chi_stat)
    print("  p-value    :", chi_p)
