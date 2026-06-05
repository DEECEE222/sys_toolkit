#!/usr/bin/env python3
"""
generate_inventory.py - Genera datos de prueba realistas para el toolkit.
Crea un inventory.csv con 1000+ servidores ficticios y un auth.log simulado.
"""

import csv
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta

from faker import Faker


fake = Faker("es_ES")
random.seed(42)

DEPARTMENTS = [
    "Desarrollo", "Finanzas", "RRHH", "Marketing",
    "Operaciones", "Seguridad", "Infraestructura", "I+D",
]

OS_LIST = [
    "Ubuntu 22.04 LTS", "Ubuntu 20.04 LTS", "Debian 12",
    "CentOS 7", "Rocky Linux 9", "RHEL 9",
    "Windows Server 2022", "Windows Server 2019", "Windows Server 2016",
]

ROLES = [
    "web", "db", "mail", "proxy", "backup",
    "monitor", "dns", "nfs", "ldap", "ci-cd",
]

STATUS_OPTIONS = ["activo", "activo", "activo", "mantenimiento", "degradado"]


def random_ip() -> str:
    return f"10.{random.randint(0,5)}.{random.randint(0,255)}.{random.randint(1,254)}"


def random_mac() -> str:
    return ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))


def random_date(start_days_ago: int = 730, end_days_ago: int = 0) -> str:
    delta = timedelta(days=random.randint(end_days_ago, start_days_ago))
    return (datetime.now() - delta).strftime("%Y-%m-%d")


def generate_inventory(path: str = "data/inventory.csv", rows: int = 1000) -> None:
    """
    Genera un archivo CSV con servidores ficticios.

    Args:
        path: Ruta de salida del archivo CSV.
        rows: Número de filas a generar (por defecto 1000).
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "hostname", "ip", "mac", "os", "ram_gb", "cpu_cores",
        "disk_gb", "department", "role", "status",
        "last_patch", "purchase_date", "admin_email",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, rows + 1):
            dept = random.choice(DEPARTMENTS)
            os_name = random.choice(OS_LIST)
            ram = random.choice([2, 4, 4, 8, 8, 16, 32, 64])

            writer.writerow({
                "hostname": f"srv-{dept[:3].lower()}-{i:04d}",
                "ip": random_ip(),
                "mac": random_mac(),
                "os": os_name,
                "ram_gb": ram,
                "cpu_cores": random.choice([2, 4, 4, 8, 8, 16]),
                "disk_gb": random.choice([100, 250, 500, 500, 1000, 2000]),
                "department": dept,
                "role": random.choice(ROLES),
                "status": random.choice(STATUS_OPTIONS),
                "last_patch": random_date(365, 0),
                "purchase_date": random_date(1825, 365),
                "admin_email": fake.email(),
            })

    print(f"  ✅ Inventario generado: {path} ({rows} servidores)")


def generate_auth_log(path: str = "data/auth.log", lines: int = 3000) -> None:
    """
    Genera un archivo auth.log simulado con intentos SSH fallidos y exitosos.

    Args:
        path: Ruta de salida del archivo auth.log.
        lines: Número aproximado de líneas a generar.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    # IPs atacantes (pocas IPs, muchos intentos = comportamiento real de brute-force)
    attacker_ips = [
        f"{random.randint(1,220)}.{random.randint(1,254)}."
        f"{random.randint(1,254)}.{random.randint(1,254)}"
        for _ in range(20)
    ]
    # IPs legítimas (muchas IPs, pocos intentos)
    legit_ips = [f"10.0.{random.randint(0,5)}.{random.randint(1,50)}" for _ in range(10)]

    users_fail = ["root", "admin", "ubuntu", "pi", "oracle", "test", "deploy"]
    users_ok = ["jdoe", "msmith", "cgarcia", "deploy", "ansible"]

    now = datetime.now()
    log_lines: list[str] = []

    for i in range(lines):
        ts = (now - timedelta(seconds=random.randint(0, 86400 * 7))).strftime(
            "%b %d %H:%M:%S"
        )
        pid = random.randint(10000, 99999)

        if random.random() < 0.80:
            # 80% fallos desde IPs atacantes
            ip = random.choice(attacker_ips)
            user = random.choice(users_fail)
            invalid = "invalid user " if random.random() < 0.4 else ""
            port = random.randint(40000, 65000)
            line = (
                f"{ts} webserver01 sshd[{pid}]: Failed password for "
                f"{invalid}{user} from {ip} port {port} ssh2"
            )
        elif random.random() < 0.10:
            # 10% accesos exitosos desde IPs legítimas
            ip = random.choice(legit_ips)
            user = random.choice(users_ok)
            port = random.randint(40000, 65000)
            method = random.choice(["password", "publickey"])
            line = (
                f"{ts} webserver01 sshd[{pid}]: Accepted {method} for "
                f"{user} from {ip} port {port} ssh2"
            )
        else:
            # Otras líneas de syslog
            messages = [
                f"{ts} webserver01 sshd[{pid}]: Connection closed by {random.choice(attacker_ips)}",
                f"{ts} webserver01 sudo[{pid}]: jdoe : TTY=pts/0 ; COMMAND=/usr/bin/apt update",
                f"{ts} webserver01 sshd[{pid}]: Disconnected from {random.choice(legit_ips)}",
            ]
            line = random.choice(messages)

        log_lines.append(line)

    # Ordenar por timestamp (aproximado)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    print(f"  ✅ Log de autenticación generado: {path} ({lines} líneas)")


if __name__ == "__main__":
    generate_logs = "--logs" in sys.argv or "--all" in sys.argv
    generate_inv = "--inventory" in sys.argv or "--all" in sys.argv or len(sys.argv) == 1

    print("\n  🏭 Generador de datos de prueba - SYS TOOLKIT\n")

    if generate_inv:
        generate_inventory()

    if generate_logs or len(sys.argv) == 1:
        generate_auth_log()

    print("\n  Datos listos en el directorio data/\n")
