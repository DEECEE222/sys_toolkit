#!/usr/bin/env python3
"""
tests/test_toolkit.py - Tests unitarios para el SYS TOOLKIT.
Verifica el correcto funcionamiento de los módulos principales.
"""

import sys
import os
import tempfile
from pathlib import Path

import pytest

# Añadir el directorio padre al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from log_parser import parse_auth_log, count_failed_ips
from os_utils import check_ping, check_disk_space
from network_models import Router, Server, Switch


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_auth_log(tmp_path: Path) -> str:
    """Crea un auth.log de prueba con IPs conocidas."""
    log_content = """Jun  5 10:00:01 webserver01 sshd[12345]: Failed password for root from 192.168.1.100 port 54321 ssh2
Jun  5 10:00:02 webserver01 sshd[12346]: Failed password for invalid user admin from 10.0.0.50 port 54322 ssh2
Jun  5 10:00:03 webserver01 sshd[12347]: Failed password for root from 192.168.1.100 port 54323 ssh2
Jun  5 10:00:04 webserver01 sshd[12348]: Failed password for root from 192.168.1.100 port 54324 ssh2
Jun  5 10:00:05 webserver01 sshd[12349]: Accepted password for jdoe from 10.0.0.1 port 54325 ssh2
Jun  5 10:00:06 webserver01 sshd[12350]: Failed password for ubuntu from 172.16.0.5 port 54326 ssh2
Jun  5 10:00:07 webserver01 sshd[12351]: Failed password for invalid user oracle from 10.0.0.50 port 54327 ssh2
"""
    log_file = tmp_path / "auth.log"
    log_file.write_text(log_content, encoding="utf-8")
    return str(log_file)


# ─── Tests: log_parser ───────────────────────────────────────────────────────

class TestLogParser:
    """Tests para el módulo log_parser.py"""

    def test_parse_auth_log_returns_set(self, sample_auth_log: str) -> None:
        """parse_auth_log debe devolver un set."""
        result = parse_auth_log(sample_auth_log)
        assert isinstance(result, set)

    def test_parse_auth_log_correct_ips(self, sample_auth_log: str) -> None:
        """Debe extraer exactamente las IPs con fallos de login."""
        result = parse_auth_log(sample_auth_log)
        expected = {"192.168.1.100", "10.0.0.50", "172.16.0.5"}
        assert result == expected

    def test_parse_auth_log_no_duplicates(self, sample_auth_log: str) -> None:
        """El Set debe eliminar duplicados (192.168.1.100 aparece 3 veces)."""
        result = parse_auth_log(sample_auth_log)
        # La IP 192.168.1.100 aparece 3 veces pero en el Set solo debe estar 1 vez
        assert len([ip for ip in result if ip == "192.168.1.100"]) == 1

    def test_parse_auth_log_excludes_accepted(self, sample_auth_log: str) -> None:
        """Las IPs de login aceptado NO deben aparecer en los fallos."""
        result = parse_auth_log(sample_auth_log)
        # 10.0.0.1 solo tiene un Accepted, no debe aparecer en fallos
        assert "10.0.0.1" not in result

    def test_parse_auth_log_file_not_found(self) -> None:
        """Debe lanzar FileNotFoundError si el archivo no existe."""
        with pytest.raises(FileNotFoundError):
            parse_auth_log("/ruta/que/no/existe/auth.log")

    def test_count_failed_ips_structure(self, sample_auth_log: str) -> None:
        """count_failed_ips debe devolver un diccionario."""
        failed_ips = parse_auth_log(sample_auth_log)
        result = count_failed_ips(failed_ips, log_path=sample_auth_log)
        assert isinstance(result, dict)

    def test_count_failed_ips_correct_counts(self, sample_auth_log: str) -> None:
        """Las IPs deben tener el conteo correcto de intentos."""
        failed_ips = parse_auth_log(sample_auth_log)
        result = count_failed_ips(failed_ips, log_path=sample_auth_log)
        # 192.168.1.100 aparece 3 veces en el log de prueba
        assert result["192.168.1.100"] == 3
        # 10.0.0.50 aparece 2 veces
        assert result["10.0.0.50"] == 2
        # 172.16.0.5 aparece 1 vez
        assert result["172.16.0.5"] == 1

    def test_count_failed_ips_all_ips_present(self, sample_auth_log: str) -> None:
        """Todas las IPs del set deben estar en el diccionario resultado."""
        failed_ips = parse_auth_log(sample_auth_log)
        result = count_failed_ips(failed_ips, log_path=sample_auth_log)
        for ip in failed_ips:
            assert ip in result

    def test_parse_empty_log(self, tmp_path: Path) -> None:
        """Un archivo de log vacío debe devolver un set vacío."""
        empty_log = tmp_path / "empty.log"
        empty_log.write_text("", encoding="utf-8")
        result = parse_auth_log(str(empty_log))
        assert result == set()

    def test_parse_log_no_failures(self, tmp_path: Path) -> None:
        """Un log sin fallos debe devolver un set vacío."""
        log_content = "Jun  5 10:00:05 webserver01 sshd[12349]: Accepted password for jdoe from 10.0.0.1 port 54325 ssh2\n"
        log_file = tmp_path / "clean.log"
        log_file.write_text(log_content, encoding="utf-8")
        result = parse_auth_log(str(log_file))
        assert result == set()


# ─── Tests: os_utils ─────────────────────────────────────────────────────────

class TestOsUtils:
    """Tests para el módulo os_utils.py"""

    def test_check_ping_localhost(self) -> None:
        """El localhost debe responder siempre al ping."""
        assert check_ping("127.0.0.1") is True

    def test_check_ping_invalid_ip(self) -> None:
        """Una IP de formato inválido debe devolver False."""
        result = check_ping("999.999.999.999")
        assert result is False

    def test_check_ping_returns_bool(self) -> None:
        """check_ping debe devolver siempre un booleano."""
        result = check_ping("127.0.0.1")
        assert isinstance(result, bool)

    def test_check_disk_space_valid_path(self, capsys) -> None:
        """check_disk_space no debe lanzar excepción para '/'."""
        check_disk_space("/")
        captured = capsys.readouterr()
        assert "Total" in captured.out

    def test_check_disk_space_invalid_path(self, capsys) -> None:
        """check_disk_space debe informar si la ruta no existe."""
        check_disk_space("/ruta/que/no/existe")
        captured = capsys.readouterr()
        assert "no existe" in captured.out


# ─── Tests: network_models ───────────────────────────────────────────────────

class TestNetworkModels:
    """Tests para el módulo network_models.py"""

    def test_router_creation(self) -> None:
        """Se debe poder crear un Router con los atributos correctos."""
        r = Router(hostname="gw01", ip="10.0.0.1", mac="aa:bb:cc:dd:ee:ff", model="Cisco ISR4321")
        assert r.hostname == "gw01"
        assert r.ip == "10.0.0.1"
        assert r.model == "Cisco ISR4321"

    def test_server_creation(self) -> None:
        """Se debe poder crear un Server con los atributos correctos."""
        s = Server(hostname="web01", ip="10.0.1.10", mac="aa:bb:cc:00:11:22", ram_gb=16)
        assert s.ram_gb == 16
        assert s.os_name == "Linux"

    def test_switch_creation(self) -> None:
        """Se debe poder crear un Switch."""
        sw = Switch(hostname="sw-core01", ip="10.0.0.2", mac="11:22:33:44:55:66", port_count=48)
        assert sw.port_count == 48

    def test_router_audit_device_runs(self, capsys) -> None:
        """audit_device() del Router debe imprimir sin errores."""
        r = Router(hostname="gw01", ip="10.0.0.1", mac="aa:bb:cc:dd:ee:ff")
        r.audit_device()
        captured = capsys.readouterr()
        assert "AUDITORÍA DE ROUTER" in captured.out

    def test_server_audit_device_runs(self, capsys) -> None:
        """audit_device() del Server debe imprimir sin errores."""
        s = Server(hostname="web01", ip="10.0.1.10", mac="aa:bb:cc:00:11:22")
        s.audit_device()
        captured = capsys.readouterr()
        assert "AUDITORÍA DE SERVIDOR" in captured.out

    def test_server_low_ram_warning(self, capsys) -> None:
        """Un servidor con < 4 GB debe mostrar una alerta de RAM."""
        s = Server(hostname="old01", ip="10.0.1.99", mac="ff:ee:dd:cc:bb:aa", ram_gb=2)
        s.audit_device()
        captured = capsys.readouterr()
        assert "RAM MUY BAJA" in captured.out

    def test_server_windows_extra_checks(self, capsys) -> None:
        """Un servidor Windows debe mostrar directrices adicionales."""
        s = Server(
            hostname="win01", ip="10.0.2.10", mac="aa:00:bb:11:cc:22",
            os_name="Windows Server 2022"
        )
        s.audit_device()
        captured = capsys.readouterr()
        assert "Windows Defender" in captured.out

    def test_polymorphism(self, capsys) -> None:
        """El método audit_device() se comporta distinto según el tipo."""
        devices = [
            Router("gw01", "10.0.0.1", "aa:bb:cc:dd:ee:01"),
            Server("web01", "10.0.0.2", "aa:bb:cc:dd:ee:02"),
            Switch("sw01", "10.0.0.3", "aa:bb:cc:dd:ee:03"),
        ]
        outputs = []
        for device in devices:
            device.audit_device()
            captured = capsys.readouterr()
            outputs.append(captured.out)

        # Cada dispositivo produce una salida diferente (polimorfismo)
        assert outputs[0] != outputs[1]
        assert outputs[1] != outputs[2]

    def test_repr(self) -> None:
        """__repr__ debe contener el nombre de la clase y atributos clave."""
        r = Router(hostname="gw01", ip="10.0.0.1", mac="aa:bb:cc:dd:ee:ff")
        r_repr = repr(r)
        assert "Router" in r_repr
        assert "gw01" in r_repr
