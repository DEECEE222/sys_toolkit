#!/usr/bin/env python3
"""
os_utils.py - Utilidades de automatización del sistema operativo
Usa subprocess, os y shutil para interactuar con el SO.
"""

import os
import shutil
import subprocess


def check_ping(ip: str) -> bool:
    """
    Envía un único ping al host indicado.

    Args:
        ip: Dirección IP o hostname destino.

    Returns:
        True si el host responde, False en caso contrario.
    """
    try:
        import platform
        if platform.system() == "Windows":
            cmd = ["ping", "-n", "1", "-w", "2000", ip]
        else:
            cmd = ["ping", "-c", "1", "-W", "2", ip]
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  [!] Timeout alcanzado para {ip}")
        return False
    except FileNotFoundError:
        print("  [!] Comando 'ping' no encontrado en el sistema.")
        return False


def check_disk_space(path: str = "/", threshold_pct: float = 20.0) -> None:
    """
    Comprueba el espacio libre en disco de una partición.
    Lanza una alerta si el espacio libre es menor al umbral indicado.

    Args:
        path: Ruta de la partición a comprobar (por defecto '/').
        threshold_pct: Porcentaje mínimo de espacio libre aceptable.
    """
    if not os.path.exists(path):
        print(f"  [!] La ruta '{path}' no existe.")
        return

    usage: shutil.disk_usage = shutil.disk_usage(path)
    total_gb: float = usage.total / (1024 ** 3)
    used_gb: float = usage.used / (1024 ** 3)
    free_gb: float = usage.free / (1024 ** 3)
    free_pct: float = (usage.free / usage.total) * 100

    print(f"\n  📂 Partición: {path}")
    print(f"  Total : {total_gb:.1f} GB")
    print(f"  Usado : {used_gb:.1f} GB")
    print(f"  Libre : {free_gb:.1f} GB ({free_pct:.1f}%)")

    if free_pct < threshold_pct:
        print(
            f"\n  ⚠️  ALERTA: Espacio libre ({free_pct:.1f}%) por debajo del "
            f"umbral ({threshold_pct:.0f}%). ¡Limpia el disco!"
        )
    else:
        print(f"\n  ✅ Espacio libre suficiente (umbral: {threshold_pct:.0f}%)")
