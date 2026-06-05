#!/usr/bin/env python3
"""
sys_toolkit.py - Kit de herramientas para administradores de sistemas (ASIR)
Fase 7: Automatización y análisis de redes con Python
"""

from os_utils import check_ping, check_disk_space
from log_parser import parse_auth_log, count_failed_ips
from threat_intel import enrich_ips_table
from inventory_manager import run_inventory_analysis
from report_generator import generate_excel_report


def print_banner() -> None:
    banner = """
╔══════════════════════════════════════════════════╗
║        SYS TOOLKIT v1.0 - ASIR Fase 7           ║
║   Automatización y análisis de redes con Python  ║
╚══════════════════════════════════════════════════╝
"""
    print(banner)


def print_menu() -> None:
    menu = """
┌─────────────────────────────────────────────────┐
│                   MENÚ PRINCIPAL                │
├─────────────────────────────────────────────────┤
│  1. Comprobar conectividad (ping a una IP)      │
│  2. Verificar espacio en disco                  │
│  3. Analizar auth.log (auditoría SSH)           │
│  4. Enriquecer IPs con threat intelligence      │
│  5. Gestionar inventario de red (CSV → Pandas)  │
│  6. Generar informe Excel ejecutivo             │
│  0. Salir                                       │
└─────────────────────────────────────────────────┘
"""
    print(menu)


def handle_ping() -> None:
    ip: str = input("  Introduce la IP o hostname a comprobar: ").strip()
    if not ip:
        print("  [!] IP vacía, operación cancelada.")
        return
    result: bool = check_ping(ip)
    status = "✅ RESPONDE" if result else "❌ SIN RESPUESTA"
    print(f"  → {ip}: {status}")


def handle_disk() -> None:
    path: str = input("  Ruta de la partición (por defecto '/'): ").strip() or "/"
    check_disk_space(path)


def handle_log_parser() -> None:
    log_path: str = input(
        "  Ruta del auth.log (por defecto 'data/auth.log'): "
    ).strip() or "data/auth.log"
    failed_ips = parse_auth_log(log_path)
    counts = count_failed_ips(failed_ips)
    print(f"\n  📊 IPs únicas con fallos de login: {len(counts)}")
    print(f"  {'IP':<20} {'Intentos':>10}")
    print(f"  {'-'*20}  {'-'*10}")
    for ip, attempts in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {ip:<20} {attempts:>10}")


def handle_threat_intel() -> None:
    log_path: str = input(
        "  Ruta del auth.log (por defecto 'data/auth.log'): "
    ).strip() or "data/auth.log"
    failed_ips = parse_auth_log(log_path)
    counts = count_failed_ips(failed_ips)
    # Tomar las 5 IPs más agresivas para no agotar la API
    top_ips: dict[str, int] = dict(
        sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    )
    enrich_ips_table(top_ips)


def handle_inventory() -> None:
    csv_path: str = input(
        "  Ruta del CSV de inventario (por defecto 'data/inventory.csv'): "
    ).strip() or "data/inventory.csv"
    run_inventory_analysis(csv_path)


def handle_report() -> None:
    csv_path: str = input(
        "  Ruta del CSV de inventario (por defecto 'data/inventory.csv'): "
    ).strip() or "data/inventory.csv"
    output_path: str = input(
        "  Ruta del Excel de salida (por defecto 'reports/informe.xlsx'): "
    ).strip() or "reports/informe.xlsx"
    generate_excel_report(csv_path, output_path)


def main() -> None:
    print_banner()
    actions: dict[str, object] = {
        "1": handle_ping,
        "2": handle_disk,
        "3": handle_log_parser,
        "4": handle_threat_intel,
        "5": handle_inventory,
        "6": handle_report,
    }

    while True:
        print_menu()
        choice: str = input("  Selecciona una opción: ").strip()

        if choice == "0":
            print("\n  👋 ¡Hasta la próxima, sysadmin!\n")
            break
        elif choice in actions:
            print()
            try:
                actions[choice]()  # type: ignore[operator]
            except KeyboardInterrupt:
                print("\n  [!] Operación cancelada por el usuario.")
            except Exception as e:
                print(f"\n  [ERROR] {e}")
        else:
            print("  [!] Opción no válida. Introduce un número del 0 al 6.")

        input("\n  Pulsa ENTER para continuar...")


if __name__ == "__main__":
    main()
