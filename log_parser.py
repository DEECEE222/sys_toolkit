#!/usr/bin/env python3
"""
log_parser.py - Parseo de auth.log para auditoría de accesos SSH.
Usa gestión de contexto (with open), operaciones de cadena y Sets/Dicts.
"""

import re
from pathlib import Path


# Patrón para extraer IP de líneas de fallo SSH
_FAILED_LOGIN_PATTERN = re.compile(
    r"Failed password for(?: invalid user)? \S+ from ([\d.]+)"
)
_ACCEPTED_LOGIN_PATTERN = re.compile(
    r"Accepted (?:password|publickey) for \S+ from ([\d.]+)"
)


def parse_auth_log(log_path: str) -> set[str]:
    """
    Lee el archivo auth.log línea a línea y extrae IPs con login fallido.

    Args:
        log_path: Ruta al archivo auth.log.

    Returns:
        Set de IPs únicas que han tenido al menos un fallo de login.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    failed_ips: set[str] = set()
    path = Path(log_path)

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de log: {log_path}\n"
            "  Ejecuta primero: python generate_inventory.py --logs"
        )

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            match = _FAILED_LOGIN_PATTERN.search(line)
            if match:
                failed_ips.add(match.group(1))

    print(f"  📄 Log analizado: {log_path}")
    print(f"  🔍 IPs únicas con fallos: {len(failed_ips)}")
    return failed_ips


def count_failed_ips(failed_ips: set[str], log_path: str | None = None) -> dict[str, int]:
    """
    Cuenta el número de intentos fallidos por IP.
    Si se proporciona log_path, relee el archivo para obtener conteos exactos.

    Args:
        failed_ips: Set de IPs a contar (usado como filtro si se da log_path).
        log_path: Ruta opcional al log original para contar intentos por IP.

    Returns:
        Diccionario {ip: número_de_intentos}.
    """
    counts: dict[str, int] = {ip: 0 for ip in failed_ips}

    # Si no tenemos el path del log original, devolvemos conteos desde el set
    if log_path is None:
        # Intentamos encontrar el log en la ubicación por defecto
        default_path = Path("data/auth.log")
        if default_path.exists():
            log_path = str(default_path)
        else:
            return {ip: 1 for ip in failed_ips}

    path = Path(log_path)
    if not path.exists():
        return {ip: 1 for ip in failed_ips}

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            match = _FAILED_LOGIN_PATTERN.search(line)
            if match:
                ip = match.group(1)
                if ip in counts:
                    counts[ip] += 1

    return counts


def get_accepted_ips(log_path: str) -> set[str]:
    """
    Extrae IPs que han tenido login exitoso.

    Args:
        log_path: Ruta al archivo auth.log.

    Returns:
        Set de IPs con logins aceptados.
    """
    accepted: set[str] = set()
    path = Path(log_path)

    if not path.exists():
        return accepted

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            match = _ACCEPTED_LOGIN_PATTERN.search(line)
            if match:
                accepted.add(match.group(1))

    return accepted
