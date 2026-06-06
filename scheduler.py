#!/usr/bin/env python3
"""
scheduler.py - Demonio de automatización del SYS TOOLKIT.
Ejecuta el informe Excel automáticamente cada mes y comprueba
el disco y los logs SSH cada hora.

Uso:
    python scheduler.py

Para detenerlo: Ctrl+C
"""

import schedule
import time
import logging
from datetime import datetime
from pathlib import Path

from report_generator import generate_excel_report
from log_parser import parse_auth_log, count_failed_ips
from os_utils import check_disk_space


# ─── Configuración de logging ─────────────────────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "scheduler.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ─── Tareas programadas ───────────────────────────────────────────────────────

def job_excel_report() -> None:
    """Genera el informe Excel mensual con timestamp en el nombre."""
    try:
        timestamp = datetime.now().strftime("%Y%m")
        output = f"reports/informe_{timestamp}.xlsx"
        log.info("Iniciando generación de informe mensual...")
        generate_excel_report("data/inventory.csv", output)
        log.info(f"Informe generado: {output}")
    except Exception as e:
        log.error(f"Error generando informe: {e}")


def job_check_disk() -> None:
    """Comprueba el espacio en disco y registra alertas."""
    try:
        log.info("Comprobando espacio en disco...")
        check_disk_space("/")
    except Exception as e:
        log.error(f"Error comprobando disco: {e}")


def job_check_logs() -> None:
    """Analiza el auth.log y registra IPs sospechosas."""
    try:
        log_path = "data/auth.log"
        log.info("Analizando auth.log en busca de ataques SSH...")
        failed_ips = parse_auth_log(log_path)
        counts = count_failed_ips(failed_ips, log_path=log_path)
        top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        log.info(f"IPs únicas con fallos: {len(counts)}")
        for ip, attempts in top:
            log.warning(f"IP sospechosa: {ip} — {attempts} intentos fallidos")
    except FileNotFoundError:
        log.error("No se encontró auth.log. Ejecuta generate_inventory.py primero.")
    except Exception as e:
        log.error(f"Error analizando logs: {e}")


# ─── Planificación ────────────────────────────────────────────────────────────

def setup_schedule() -> None:
    schedule.every(30).days.at("08:00").do(job_excel_report)
    schedule.every().hour.do(job_check_disk)
    schedule.every().hour.do(job_check_logs)

    log.info("═" * 55)
    log.info("  SYS TOOLKIT — Demonio de automatización activo")
    log.info("  Informe Excel : cada mes el día 1 a las 08:00")
    log.info("  Disco + Logs  : cada hora")
    log.info("  Para detener  : Ctrl+C")
    log.info("═" * 55)


def main() -> None:
    setup_schedule()
    log.info("Ejecutando tareas iniciales...")
    job_check_disk()
    job_check_logs()
    job_excel_report()

    log.info("Demonio en espera. Próxima ejecución programada...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Demonio detenido por el usuario.")


if __name__ == "__main__":
    main()