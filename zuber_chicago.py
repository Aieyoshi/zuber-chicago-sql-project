from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


def find_file(base_dir: Path, filename: str) -> Path:
    """
    Busca un archivo en:
    - base_dir/filename
    - base_dir/datasets/filename
    - cualquier subcarpeta (recursivo) si no aparece en los anteriores
    """
    direct = base_dir / filename
    if direct.exists():
        return direct

    datasets = base_dir / "datasets" / filename
    if datasets.exists():
        return datasets

    matches = list(base_dir.rglob(filename))
    if matches:
        return matches[0]

    raise FileNotFoundError(f"No encontré {filename} dentro de: {base_dir}")


def load_csv(base_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # acepta nombres con o sin "moved_"
    f01 = find_file(base_dir, "project_sql_result_01.csv") if (
        base_dir / "project_sql_result_01.csv").exists() else find_file(base_dir, "moved_project_sql_result_01.csv")
    f04 = find_file(base_dir, "project_sql_result_04.csv") if (
        base_dir / "project_sql_result_04.csv").exists() else find_file(base_dir, "moved_project_sql_result_04.csv")
    f07 = find_file(base_dir, "project_sql_result_07.csv") if (
        base_dir / "project_sql_result_07.csv").exists() else find_file(base_dir, "moved_project_sql_result_07.csv")

    df_01 = pd.read_csv(f01)
    df_04 = pd.read_csv(f04)
    df_07 = pd.read_csv(f07)

    print("Archivos cargados:")
    print(" -", f01)
    print(" -", f04)
    print(" -", f07)
    print()

    return df_01, df_04, df_07


def ensure_types(df_01: pd.DataFrame, df_04: pd.DataFrame, df_07: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Dataset 01
    df_01["company_name"] = df_01["company_name"].astype(str).str.strip()
    df_01["trips_amount"] = pd.to_numeric(
        df_01["trips_amount"], errors="coerce")

    # Dataset 04
    df_04["dropoff_location_name"] = df_04["dropoff_location_name"].astype(
        str).str.strip()
    df_04["average_trips"] = pd.to_numeric(
        df_04["average_trips"], errors="coerce")

    # Dataset 07
    df_07["start_ts"] = pd.to_datetime(df_07["start_ts"], errors="coerce")
    df_07["weather_conditions"] = df_07["weather_conditions"].astype(
        str).str.strip()
    df_07["duration_seconds"] = pd.to_numeric(
        df_07["duration_seconds"], errors="coerce")

    # Quitar filas con nulos en columnas clave
    df_01 = df_01.dropna(subset=["company_name", "trips_amount"])
    df_04 = df_04.dropna(subset=["dropoff_location_name", "average_trips"])
    df_07 = df_07.dropna(
        subset=["start_ts", "weather_conditions", "duration_seconds"])

    return df_01, df_04, df_07


def save_plot_company_trips(df_01: pd.DataFrame, out_dir: Path) -> None:
    df_sorted = df_01.sort_values("trips_amount", ascending=False)

    plt.figure(figsize=(12, 6))
    plt.bar(df_sorted["company_name"], df_sorted["trips_amount"])
    plt.xticks(rotation=90)
    plt.ylabel("Número de viajes (15–16 nov 2017)")
    plt.title("Viajes por empresa de taxi")
    plt.tight_layout()

    out_path = out_dir / "plot_01_company_trips.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("Gráfica guardada:", out_path)


def save_plot_top10_dropoffs(df_04: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    top10 = df_04.sort_values("average_trips", ascending=False).head(10)
    # para barra horizontal legible
    top10_sorted = top10.sort_values("average_trips")

    plt.figure(figsize=(10, 6))
    plt.barh(top10_sorted["dropoff_location_name"],
             top10_sorted["average_trips"])
    plt.xlabel("Promedio de viajes (nov 2017)")
    plt.title("Top 10 barrios por finalización de viajes")
    plt.tight_layout()

    out_path = out_dir / "plot_04_top10_dropoffs.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print("Gráfica guardada:", out_path)

    return top10


def hypothesis_test(df_07: pd.DataFrame, alpha: float = 0.05, remove_nonpositive: bool = True) -> None:
    # Validación rápida: ¿solo sábados?
    # Monday=0 ... Saturday=5 ... Sunday=6
    saturday_ratio = (df_07["start_ts"].dt.dayofweek == 5).mean()
    print(f"Proporción de sábados en el dataset: {saturday_ratio:.3f}")

    # Limpieza opcional (recomendado): remover duraciones no realistas
    if remove_nonpositive:
        before = len(df_07)
        df_07 = df_07[df_07["duration_seconds"] > 0].copy()
        after = len(df_07)
        print(f"Filtrado duration_seconds > 0: {before} -> {after}")

    bad = df_07.loc[df_07["weather_conditions"] == "Bad", "duration_seconds"]
    good = df_07.loc[df_07["weather_conditions"] == "Good", "duration_seconds"]

    print("\nTamaños de muestra:")
    print("n_Bad :", len(bad))
    print("n_Good:", len(good))

    print("\nEstadísticos descriptivos (duración en segundos):")
    print("Bad:\n", bad.describe())
    print("\nGood:\n", good.describe())

    # Welch t-test (no asumimos varianzas iguales)
    t_stat, p_value = stats.ttest_ind(bad, good, equal_var=False)

    print("\nPrueba t (Welch):")
    print("t-statistic:", t_stat)
    print("p-value:", p_value)

    diff = bad.mean() - good.mean()
    print(
        f"\nDiferencia de medias (Bad - Good): {diff:.2f} s (~{diff/60:.2f} min)")

    print("\nDecisión (alpha = {:.2f}):".format(alpha))
    if p_value < alpha:
        print("Rechazamos H0: hay evidencia de que la duración promedio CAMBIA entre Bad y Good.")
        print("Además, la media en Bad es MAYOR que en Good (viajes más largos con mal clima).")
    else:
        print("No rechazamos H0: no hay evidencia suficiente de cambio en la duración promedio.")


def main() -> int:
    # Cambia esta ruta si mueves la carpeta
    base_dir = Path(r"C:\Users\alehe\Documents\TripleTen\Spring 8\project_8")

    if not base_dir.exists():
        print("No existe la ruta base:", base_dir)
        return 1

    out_dir = base_dir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    df_01, df_04, df_07 = load_csv(base_dir)
    df_01, df_04, df_07 = ensure_types(df_01, df_04, df_07)

    print("=== Dataset 01 info ===")
    print(df_01.head())
    print(df_01.info())
    print()

    print("=== Dataset 04 info ===")
    print(df_04.head())
    print(df_04.info())
    print()

    print("=== Dataset 07 info ===")
    print(df_07.head())
    print(df_07.info())
    print()

    # Top 10 y plots
    save_plot_company_trips(df_01, out_dir)
    top10 = save_plot_top10_dropoffs(df_04, out_dir)

    print("\nTop 10 dropoff locations:")
    print(top10.to_string(index=False))

    # Prueba de hipótesis
    print("\n=== Prueba de hipótesis (Dataset 07) ===")
    hypothesis_test(df_07, alpha=0.05, remove_nonpositive=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
