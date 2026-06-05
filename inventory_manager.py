#!/usr/bin/env python3
"""
inventory_manager.py - Gestión y análisis de inventarios de red con Pandas.
Filtra, agrupa y analiza el inventario de servidores.
"""

from pathlib import Path

import pandas as pd


def load_inventory(csv_path: str) -> pd.DataFrame:
    """
    Carga el inventario desde un archivo CSV.

    Args:
        csv_path: Ruta al archivo CSV.

    Returns:
        DataFrame con el inventario cargado.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el inventario: {csv_path}\n"
            "  Ejecuta primero: python generate_inventory.py"
        )

    df = pd.read_csv(csv_path)
    print(f"  📂 Inventario cargado: {len(df)} servidores, {len(df.columns)} columnas")
    return df


def filter_windows_servers(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra los servidores que ejecutan Windows Server."""
    mask = df["os"].str.contains("Windows", case=False, na=False)
    result = df[mask].copy()
    print(f"  🪟 Servidores Windows Server encontrados: {len(result)}")
    return result


def filter_low_ram(df: pd.DataFrame, threshold_gb: int = 4) -> pd.DataFrame:
    """Filtra los servidores con RAM menor al umbral indicado."""
    result = df[df["ram_gb"] < threshold_gb].copy()
    print(f"  💾 Servidores con menos de {threshold_gb} GB de RAM: {len(result)}")
    return result


def filter_vulnerable_servers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra servidores potencialmente vulnerables:
    - Windows Server (objetivo frecuente)
    - Menos de 4 GB de RAM
    - Estado 'degradado'
    - Sin parche en los últimos 180 días
    """
    df_copy = df.copy()
    df_copy["last_patch"] = pd.to_datetime(df_copy["last_patch"], errors="coerce")
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=180)

    mask = (
        df_copy["os"].str.contains("Windows", case=False, na=False)
        | (df_copy["ram_gb"] < 4)
        | (df_copy["status"] == "degradado")
        | (df_copy["last_patch"] < cutoff)
    )
    result = df_copy[mask].copy()
    print(f"  🚨 Servidores vulnerables o desactualizados: {len(result)}")
    return result


def group_by_department(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa los servidores por departamento y cuenta cuántos tiene cada área.

    Returns:
        DataFrame con el recuento por departamento.
    """
    summary = (
        df.groupby("department")
        .agg(
            total_servidores=("hostname", "count"),
            ram_media_gb=("ram_gb", "mean"),
            windows=("os", lambda x: x.str.contains("Windows", case=False).sum()),
            linux=("os", lambda x: (~x.str.contains("Windows", case=False)).sum()),
        )
        .sort_values("total_servidores", ascending=False)
        .reset_index()
    )
    summary["ram_media_gb"] = summary["ram_media_gb"].round(1)
    return summary


def run_inventory_analysis(csv_path: str) -> None:
    """
    Ejecuta el análisis completo del inventario y muestra los resultados.

    Args:
        csv_path: Ruta al archivo CSV del inventario.
    """
    df = load_inventory(csv_path)

    print("\n  ─── Estadísticas generales ─────────────────────────────")
    print(f"  Total servidores : {len(df)}")
    print(f"  RAM media        : {df['ram_gb'].mean():.1f} GB")
    print(f"  Sistemas Windows : {df['os'].str.contains('Windows').sum()}")
    print(f"  Sistemas Linux   : {(~df['os'].str.contains('Windows')).sum()}")
    print(f"  Servidores activos: {(df['status'] == 'activo').sum()}")

    print("\n  ─── Servidores Windows Server ───────────────────────────")
    win_df = filter_windows_servers(df)
    print(win_df[["hostname", "ip", "os", "ram_gb", "department", "status"]].head(10).to_string(index=False))

    print("\n  ─── Servidores con menos de 4 GB de RAM ─────────────────")
    low_ram_df = filter_low_ram(df, 4)
    print(low_ram_df[["hostname", "ip", "ram_gb", "os", "department"]].head(10).to_string(index=False))

    print("\n  ─── Servidores por departamento ─────────────────────────")
    dept_df = group_by_department(df)
    print(dept_df.to_string(index=False))
