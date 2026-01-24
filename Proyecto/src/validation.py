# src/validation.py
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, Tuple, List

import numpy as np
import pandas as pd
from scipy import stats

from src.config import make_base_config, DistSpec


# -----------------------------
# Helpers
# -----------------------------
def _get_rv(spec: DistSpec):
    """Crea un objeto de distribución de scipy.stats a partir de DistSpec."""
    if not hasattr(stats, spec.name):
        raise ValueError(f"Distribución '{spec.name}' no existe en scipy.stats.")
    dist = getattr(stats, spec.name)
    rv = dist(*spec.shape, loc=spec.loc, scale=spec.scale)
    return rv


def _merge_small_bins(obs: np.ndarray, exp: np.ndarray, min_expected: float = 5.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Une bins cuando el esperado es < min_expected (regla típica para Chi²).
    Estrategia simple: combina el bin más pequeño con un vecino.
    """
    obs = obs.astype(float).copy()
    exp = exp.astype(float).copy()

    while len(exp) > 2:
        idx = int(np.argmin(exp))
        if exp[idx] >= min_expected:
            break

        # elegir vecino (izq o der) con menor esperado para combinar
        if idx == 0:
            j = 1
        elif idx == len(exp) - 1:
            j = len(exp) - 2
        else:
            j = idx - 1 if exp[idx - 1] <= exp[idx + 1] else idx + 1

        # combinar idx y j (deja el menor índice)
        i1, i2 = sorted([idx, j])
        obs[i1] += obs[i2]
        exp[i1] += exp[i2]
        obs = np.delete(obs, i2)
        exp = np.delete(exp, i2)

    return obs, exp


def ks_test(sample: np.ndarray, spec: DistSpec) -> Tuple[float, float]:
    """Kolmogorov–Smirnov para una distribución continua especificada."""
    rv = _get_rv(spec)
    res = stats.kstest(sample, rv.cdf)
    return float(res.statistic), float(res.pvalue)


def chi_square_test(sample: np.ndarray, spec: DistSpec, n_bins: int = 12, min_expected: float = 5.0) -> Tuple[float, int, float, int]:
    """
    Chi-cuadrado para distribución continua:
    - Crea cortes por cuantiles teóricos (ppf) para tener bins con esperado ~ igual.
    - Calcula esperados via CDF.
    - Une bins si el esperado < 5.
    Retorna: (chi2_stat, df, pvalue, bins_usados)
    """
    rv = _get_rv(spec)
    n = len(sample)

    # Evitar ppf(0)= -inf o ppf(1)=inf
    eps = 1e-3
    qs = np.linspace(eps, 1 - eps, n_bins - 1)
    inner_edges = rv.ppf(qs)

    # edges con -inf e inf para cubrir toda la masa de probabilidad
    edges = np.concatenate(([-np.inf], inner_edges, [np.inf]))

    obs, _ = np.histogram(sample, bins=edges)
    exp = []
    for i in range(len(edges) - 1):
        p = rv.cdf(edges[i + 1]) - rv.cdf(edges[i])
        exp.append(n * p)
    exp = np.array(exp, dtype=float)

    # Unir bins que no cumplen esperado mínimo
    obs2, exp2 = _merge_small_bins(obs, exp, min_expected=min_expected)

    # Evitar divisiones por 0
    mask = exp2 > 0
    chi2_stat = np.sum((obs2[mask] - exp2[mask]) ** 2 / exp2[mask])

    df = int(np.sum(mask) - 1)  # parámetros NO estimados aquí (se asumen dados)
    pvalue = float(stats.chi2.sf(chi2_stat, df)) if df > 0 else float("nan")
    bins_used = int(len(exp2))

    return float(chi2_stat), df, pvalue, bins_used


def validate_distribution(name: str, spec: DistSpec, n: int, rng: np.random.Generator) -> Dict:
    rv = _get_rv(spec)
    sample = rv.rvs(size=n, random_state=rng)

    ks_stat, ks_p = ks_test(sample, spec)
    chi2_stat, chi2_df, chi2_p, bins_used = chi_square_test(sample, spec, n_bins=12, min_expected=5.0)

    return {
        "variable": name,
        "dist_name": spec.name,
        "shape": spec.shape,
        "loc": spec.loc,
        "scale": spec.scale,
        "units": spec.units,
        "n": n,
        "ks_stat": ks_stat,
        "ks_pvalue": ks_p,
        "chi2_stat": chi2_stat,
        "chi2_df": chi2_df,
        "chi2_pvalue": chi2_p,
        "chi2_bins_used": bins_used,
    }


def main():
    cfg = make_base_config()

    project_root = Path(__file__).resolve().parents[1]  # .../Proyecto
    out_dir = project_root / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(cfg.settings.seed)

    # Qué validar
    items = [("llegadas", cfg.arrival_dist)]
    for st, spec in cfg.service_dists.items():
        items.append((f"servicio_{st}", spec))

    results = []
    n_sample = 2000  # tamaño de muestra para validar distribuciones

    for name, spec in items:
        res = validate_distribution(name, spec, n=n_sample, rng=rng)
        results.append(res)

    df = pd.DataFrame(results)
    csv_path = out_dir / "validation_results.csv"
    xlsx_path = out_dir / "validation_results.xlsx"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)

    print("✅ Validación terminada.")
    print(f" - CSV:  {csv_path}")
    print(f" - Excel:{xlsx_path}")
    print("\nResumen (p-values):")
    print(df[["variable", "ks_pvalue", "chi2_pvalue"]])


if __name__ == "__main__":
    main()
