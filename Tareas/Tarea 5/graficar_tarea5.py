# graficar_tarea5.py
# Ejecuta sim_tarea5.py y genera gráficas PNG a partir de los CSV.

from __future__ import annotations

import sys
import subprocess
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# -----------------------------
# Helpers
# -----------------------------
def read_csv_safe(path: Path) -> pd.DataFrame:
    """Lee CSV con fallback de encoding."""
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")
    # Normaliza nombres de columnas
    df.columns = [str(c).strip() for c in df.columns]
    return df


def cfg_string_from_row(row: pd.Series, cfg_cols: list[str]) -> str:
    vals = tuple(int(row[c]) for c in cfg_cols)
    return f"{vals}"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Paso 1: correr simulación
# -----------------------------
def run_simulation(script_path: Path, out_txt: Path) -> None:
    cmd = [sys.executable, str(script_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_txt.write_text(
        f"=== Salida de {script_path.name} ===\n"
        f"Fecha: {stamp}\n\n"
        f"--- STDOUT ---\n{result.stdout}\n\n"
        f"--- STDERR ---\n{result.stderr}\n",
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Error ejecutando {script_path.name}. Revisá {out_txt.name}.\n"
            f"Return code: {result.returncode}"
        )


# -----------------------------
# Paso 2: gráficas principales
# -----------------------------
def plot_top_by_W(df: pd.DataFrame, figdir: Path, cfg_cols: list[str]) -> None:
    if "W_sim" not in df.columns:
        return

    d = df.copy()
    d["cfg"] = d.apply(lambda r: cfg_string_from_row(r, cfg_cols), axis=1)
    d = d.sort_values("W_sim", ascending=True).head(15)

    x = np.arange(len(d))
    plt.figure()
    plt.bar(x, d["W_sim"].values)

    # Si hay IC, agrega barras de error
    if "IC_low" in d.columns and "IC_high" in d.columns:
        y = d["W_sim"].values
        low = y - d["IC_low"].values
        high = d["IC_high"].values - y
        yerr = np.vstack([low, high])
        plt.errorbar(x, y, yerr=yerr, fmt="none", capsize=3)

    plt.xticks(x, d["cfg"].values, rotation=45, ha="right")
    plt.ylabel("W̄ (min)")
    plt.title("Top 15 configuraciones con menor W̄")
    plt.tight_layout()
    plt.savefig(figdir / "top15_menor_W.png", dpi=200)
    plt.close()


def plot_top_by_VarW(df: pd.DataFrame, figdir: Path, cfg_cols: list[str]) -> None:
    if "Var_W" not in df.columns:
        return

    d = df.copy()
    d["cfg"] = d.apply(lambda r: cfg_string_from_row(r, cfg_cols), axis=1)
    d = d.sort_values("Var_W", ascending=True).head(15)

    x = np.arange(len(d))
    plt.figure()
    plt.bar(x, d["Var_W"].values)
    plt.xticks(x, d["cfg"].values, rotation=45, ha="right")
    plt.ylabel("Var(W) (min²)")
    plt.title("Top 15 configuraciones con menor Var(W)")
    plt.tight_layout()
    plt.savefig(figdir / "top15_menor_VarW.png", dpi=200)
    plt.close()


def plot_pareto(df: pd.DataFrame, figdir: Path, cfg_cols: list[str]) -> None:
    if "W_sim" not in df.columns or "Var_W" not in df.columns:
        return

    d = df.copy()
    d["cfg"] = d.apply(lambda r: cfg_string_from_row(r, cfg_cols), axis=1)

    plt.figure()
    plt.scatter(d["W_sim"], d["Var_W"], s=12)
    plt.xlabel("W̄ (min)")
    plt.ylabel("Var(W) (min²)")
    plt.title("Pareto: W̄ vs Var(W)")
    plt.tight_layout()
    plt.savefig(figdir / "pareto_W_vs_VarW.png", dpi=200)
    plt.close()


def plot_violations(df: pd.DataFrame, figdir: Path) -> None:
    col = None
    for candidate in ["viol_rho", "viol", "violaciones", "viol_rho_something"]:
        if candidate in df.columns:
            col = candidate
            break
    # Si no encuentra, intenta por nombre parcial
    if col is None:
        for c in df.columns:
            if "viol" in c.lower():
                col = c
                break
    if col is None:
        return

    counts = df[col].value_counts().sort_index()
    x = counts.index.astype(int)
    y = counts.values

    plt.figure()
    plt.bar(x, y)
    plt.xlabel("Cantidad de estaciones con ρ >= 0.8")
    plt.ylabel("Número de configuraciones")
    plt.title("Distribución de violaciones de utilización (ρ)")
    plt.tight_layout()
    plt.savefig(figdir / "distribucion_violaciones_rho.png", dpi=200)
    plt.close()


# -----------------------------
# Paso 3: gráficas de lambda_hat
# -----------------------------
def plot_lambda_table(csv_path: Path, figdir: Path) -> None:
    df = read_csv_safe(csv_path)
    needed = {"estacion", "lambda_hat_sim", "lambda_teorico_1pEK", "ratio_sim_teorico"}
    if not needed.issubset(set(df.columns)):
        # Si vienen con nombres distintos, intentamos detectar por “contiene”
        # (pero si no calza, simplemente no graficamos)
        return

    stations = df["estacion"].astype(str).tolist()
    x = np.arange(len(stations))

    # 1) Ratio
    plt.figure()
    plt.bar(x, df["ratio_sim_teorico"].values)
    plt.xticks(x, stations, rotation=0)
    plt.ylabel("ratio (sim / teorico)")
    plt.title(f"Ratio λ̂ vs teórico — {csv_path.stem}")
    plt.tight_layout()
    plt.savefig(figdir / f"ratio_lambda_{csv_path.stem}.png", dpi=200)
    plt.close()

    # 2) Comparación λ̂ y teórico (log para que quepan si hay desbalance)
    plt.figure()
    width = 0.38
    plt.bar(x - width / 2, df["lambda_hat_sim"].values, width=width, label="lambda_hat_sim")
    plt.bar(x + width / 2, df["lambda_teorico_1pEK"].values, width=width, label="lambda_teorico_1pEK")
    plt.yscale("log")
    plt.xticks(x, stations, rotation=0)
    plt.ylabel("tasa (escala log)")
    plt.title(f"λ̂ (sim) vs λ·p·E[K] (teórico) — {csv_path.stem}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figdir / f"lambda_hat_vs_teorico_{csv_path.stem}.png", dpi=200)
    plt.close()


# -----------------------------
# Main
# -----------------------------
def main() -> int:
    base = Path.cwd()
    sim_script = base / "sim_tarea5.py"
    figdir = base / "figuras"
    ensure_dir(figdir)

    # Flags simples:
    #   python graficar_tarea5.py --skip-run
    skip_run = "--skip-run" in sys.argv

    # 1) Ejecutar simulación (opcional)
    if not skip_run:
        if not sim_script.exists():
            print("No encuentro sim_tarea5.py en esta carpeta.")
            return 1
        out_txt = base / "salida_sim_tarea5.txt"
        print(f"Ejecutando {sim_script.name} ...")
        run_simulation(sim_script, out_txt)
        print(f"Listo. Salida guardada en: {out_txt.name}")

    # 2) Leer resultados_todas_configuraciones.csv
    results_csv = base / "resultados_todas_configuraciones.csv"
    if not results_csv.exists():
        # fallback por si el nombre varía
        candidates = list(base.glob("resultados*configuraciones*.csv"))
        if candidates:
            results_csv = candidates[0]

    if results_csv.exists():
        df = read_csv_safe(results_csv)

        # Detecta columnas de configuración (las 5 primeras típicamente)
        # Preferimos estas por nombre:
        preferred = ["cajas", "ref", "frei", "pos", "pol"]
        if all(c in df.columns for c in preferred):
            cfg_cols = preferred
        else:
            # fallback: toma primeras 5 columnas
            cfg_cols = list(df.columns[:5])

        plot_top_by_W(df, figdir, cfg_cols)
        plot_top_by_VarW(df, figdir, cfg_cols)
        plot_pareto(df, figdir, cfg_cols)
        plot_violations(df, figdir)
        print(f"Gráficas principales guardadas en: {figdir}/")
    else:
        print("No encontré resultados_todas_configuraciones.csv (ni variantes).")

    # 3) Tablas λ̂ vs teórico
    lambda_csvs = sorted(base.glob("lambda_hat_vs_teorico_*.csv"))
    for p in lambda_csvs:
        plot_lambda_table(p, figdir)
    if lambda_csvs:
        print("Gráficas de lambda_hat guardadas también en figuras/")

    print("✅ Listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
