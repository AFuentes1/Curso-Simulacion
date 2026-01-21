# graficar_tarea5.py
# Corre sim_tarea5.py (opcional) y grafica los CSV generados.

from __future__ import annotations

import sys
import subprocess
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def read_csv_safe(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def run_simulation(sim_script: Path, out_txt: Path) -> None:
    cmd = [sys.executable, str(sim_script)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_txt.write_text(
        f"=== Salida de {sim_script.name} ===\n"
        f"Fecha: {stamp}\n\n"
        f"--- STDOUT ---\n{result.stdout}\n\n"
        f"--- STDERR ---\n{result.stderr}\n",
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Error ejecutando {sim_script.name}. Revisá {out_txt.name}.\n"
            f"Return code: {result.returncode}"
        )


def detect_results_csv(base: Path) -> Path | None:
    p = base / "resultados_todas_configuraciones.csv"
    if p.exists():
        return p
    # fallback por si cambió nombre
    cands = sorted(base.glob("resultados*configuraciones*.csv"))
    return cands[0] if cands else None


def cfg_cols_in_results(df: pd.DataFrame) -> list[str]:
    preferred = ["cajas", "ref", "frei", "pos", "pol"]
    if all(c in df.columns for c in preferred):
        return preferred
    # fallback: primeras 5 columnas
    return list(df.columns[:5])


def cfg_string(row: pd.Series, cols: list[str]) -> str:
    return str(tuple(int(row[c]) for c in cols))


# ---------------------------
# Gráficas (resultados)
# ---------------------------
def plot_top(df: pd.DataFrame, figdir: Path, cfg_cols: list[str], metric: str, fname: str, title: str, ylabel: str, with_ci: bool = False) -> None:
    if metric not in df.columns:
        return

    d = df.copy()
    d["cfg"] = d.apply(lambda r: cfg_string(r, cfg_cols), axis=1)
    d = d.sort_values(metric, ascending=True).head(15)

    x = np.arange(len(d))
    plt.figure()
    plt.bar(x, d[metric].values)

    if with_ci and ("IC_low" in d.columns) and ("IC_high" in d.columns):
        y = d[metric].values
        low = y - d["IC_low"].values
        high = d["IC_high"].values - y
        yerr = np.vstack([low, high])
        plt.errorbar(x, y, yerr=yerr, fmt="none", capsize=3)

    plt.xticks(x, d["cfg"].values, rotation=45, ha="right")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(figdir / fname, dpi=200)
    plt.close()


def plot_pareto(df: pd.DataFrame, figdir: Path) -> None:
    # Pareto recomendado: W_profe (objetivo MIN_W) vs Var_W
    if "W_profe" not in df.columns or "Var_W" not in df.columns:
        return

    plt.figure()
    plt.scatter(df["W_profe"], df["Var_W"], s=12)
    plt.xlabel("W_profe = T / clientes (min/cliente)")
    plt.ylabel("Var(W) (min²)")
    plt.title("Pareto: W_profe vs Var(W)")
    plt.tight_layout()
    plt.savefig(figdir / "pareto_Wprofe_vs_VarW.png", dpi=200)
    plt.close()


def plot_violations(df: pd.DataFrame, figdir: Path) -> None:
    col = "viol_rho" if "viol_rho" in df.columns else None
    if col is None:
        # fallback: buscar algo que contenga "viol"
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
    plt.xlabel("Cantidad de violaciones (ρ>=0.8) combinadas sim/analítico")
    plt.ylabel("Número de configuraciones")
    plt.title("Distribución de violaciones de utilización (ρ)")
    plt.tight_layout()
    plt.savefig(figdir / "distribucion_violaciones_rho.png", dpi=200)
    plt.close()


def plot_score(df: pd.DataFrame, figdir: Path, cfg_cols: list[str]) -> None:
    if "score_total_100" not in df.columns:
        return

    d = df.copy()
    d["cfg"] = d.apply(lambda r: cfg_string(r, cfg_cols), axis=1)
    d = d.sort_values("score_total_100", ascending=False).head(15)

    x = np.arange(len(d))
    plt.figure()
    plt.bar(x, d["score_total_100"].values)
    plt.xticks(x, d["cfg"].values, rotation=45, ha="right")
    plt.ylabel("Score total (0-100)")
    plt.title("Top 15 configuraciones por score total")
    plt.tight_layout()
    plt.savefig(figdir / "top15_score_total.png", dpi=200)
    plt.close()


# ---------------------------
# Gráficas (lambda_hat)
# ---------------------------
def plot_lambda_table(csv_path: Path, figdir: Path) -> None:
    df = read_csv_safe(csv_path)

    # Nombres nuevos según tu actualización
    required = {"estacion", "lambda_hat_sim", "lambda_teorico_lpEK", "ratio_sim_teorico"}
    if not required.issubset(set(df.columns)):
        return

    stations = df["estacion"].astype(str).tolist()
    x = np.arange(len(stations))

    # 1) Ratio
    plt.figure()
    plt.bar(x, df["ratio_sim_teorico"].values)
    plt.xticks(x, stations)
    plt.ylabel("ratio (sim / teórico)")
    plt.title(f"Ratio λ̂ vs teórico — {csv_path.stem}")
    plt.tight_layout()
    plt.savefig(figdir / f"ratio_lambda_{csv_path.stem}.png", dpi=200)
    plt.close()

    # 2) Comparación λ̂ y teórico (log para que se vea aunque haya diferencias grandes)
    plt.figure()
    width = 0.38
    plt.bar(x - width / 2, df["lambda_hat_sim"].values, width=width, label="lambda_hat_sim")
    plt.bar(x + width / 2, df["lambda_teorico_lpEK"].values, width=width, label="lambda_teorico_lpEK")
    plt.yscale("log")
    plt.xticks(x, stations)
    plt.ylabel("tasa (escala log)")
    plt.title(f"λ̂ (sim) vs λ·p·E[K] (teórico) — {csv_path.stem}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figdir / f"lambda_hat_vs_teorico_{csv_path.stem}.png", dpi=200)
    plt.close()


def main() -> int:
    base = Path.cwd()
    figdir = base / "figuras"
    ensure_dir(figdir)

    skip_run = "--skip-run" in sys.argv

    # 1) Ejecutar sim (opcional)
    sim_script = base / "sim_tarea5.py"
    if not skip_run:
        if not sim_script.exists():
            print("❌ No encuentro sim_tarea5.py en esta carpeta.")
            print("   Solución: poné graficar_tarea5.py en la carpeta de la Tarea 5 donde está sim_tarea5.py")
            return 1

        out_txt = base / "salida_sim_tarea5.txt"
        print("▶ Ejecutando sim_tarea5.py ...")
        run_simulation(sim_script, out_txt)
        print(f"✅ Salida guardada en: {out_txt.name}")

    # 2) Resultados por configuración
    results_csv = detect_results_csv(base)
    if results_csv is None:
        print("⚠ No encontré resultados_todas_configuraciones.csv (ni variantes).")
    else:
        df = read_csv_safe(results_csv)
        cfg_cols = cfg_cols_in_results(df)

        # Top por W_profe (tu objetivo MIN_W)
        plot_top(
            df, figdir, cfg_cols,
            metric="W_profe",
            fname="top15_menor_Wprofe.png",
            title="Top 15 configuraciones con menor W_profe (T/clientes)",
            ylabel="W_profe (min/cliente)",
            with_ci=False
        )

        # Top por W_sim (tiempo real en sistema, con IC si existe)
        plot_top(
            df, figdir, cfg_cols,
            metric="W_sim",
            fname="top15_menor_Wsim.png",
            title="Top 15 configuraciones con menor W_sim (con IC si aplica)",
            ylabel="W_sim (min)",
            with_ci=True
        )

        # Top por Var_W
        plot_top(
            df, figdir, cfg_cols,
            metric="Var_W",
            fname="top15_menor_VarW.png",
            title="Top 15 configuraciones con menor Var(W)",
            ylabel="Var(W) (min²)",
            with_ci=False
        )

        plot_pareto(df, figdir)
        plot_violations(df, figdir)
        plot_score(df, figdir, cfg_cols)

        print(f"✅ Gráficas principales guardadas en: {figdir}/")

    # 3) Tablas lambda_hat
    lambda_csvs = sorted(base.glob("lambda_hat_vs_teorico_*.csv"))
    for p in lambda_csvs:
        plot_lambda_table(p, figdir)

    if lambda_csvs:
        print("✅ Gráficas de λ̂ guardadas en figuras/")

    print("✅ Listo. Abrí la carpeta 'figuras' para ver los PNG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
