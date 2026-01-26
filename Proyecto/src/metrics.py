# src/metrics.py
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
from scipy import stats

from src.simulation import ReplicationResult


def _ci_mean(x: np.ndarray, alpha: float = 0.05) -> Dict[str, float]:
    n = len(x)
    mean = float(np.mean(x)) if n else 0.0
    if n < 2:
        return {"mean": mean, "low": mean, "high": mean, "n": n}

    s = float(np.std(x, ddof=1))
    tcrit = float(stats.t.ppf(1 - alpha / 2, df=n - 1))
    half = tcrit * s / (n ** 0.5)
    return {"mean": mean, "low": mean - half, "high": mean + half, "n": n}


def summarize_replications(results: List[ReplicationResult], alpha: float = 0.05) -> Dict[str, Any]:
    tis = np.array([r.mean_time_in_system for r in results], dtype=float)
    wq = np.array([r.mean_queue_wait_total for r in results], dtype=float)
    wq_cash = np.array([r.mean_queue_wait_cashier for r in results], dtype=float)

    stations = results[0].per_station.keys() if results else []
    per_station = {}
    for st in stations:
        arr = np.array([r.per_station[st]["avg_queue_wait"] for r in results], dtype=float)
        per_station[st] = _ci_mean(arr, alpha)

    return {
        "time_in_system": _ci_mean(tis, alpha),
        "queue_wait_total": _ci_mean(wq, alpha),
        "queue_wait_cashier": _ci_mean(wq_cash, alpha),
        "per_station_avg_queue_wait": per_station,
        "replications": len(results),
    }