#!/usr/bin/env python3
"""
network_models.py - Modelo orientado a objetos para inventario de red.
Demuestra herencia, polimorfismo y encapsulación en el contexto ASIR.
"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class NetworkDevice(ABC):
    """
    Clase base abstracta para cualquier dispositivo de red.
    Define la interfaz común que deben implementar todos los dispositivos.
    """

    def __init__(
        self,
        hostname: str,
        ip: str,
        mac: str,
        department: str = "General",
    ) -> None:
        self.hostname: str = hostname
        self.ip: str = ip
        self.mac: str = mac
        self.department: str = department

    @abstractmethod
    def audit_device(self) -> None:
        """
        Imprime directrices de seguridad específicas para este tipo de dispositivo.
        Implementa polimorfismo: cada subclase define su propia auditoría.
        """
        ...

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"hostname='{self.hostname}', ip='{self.ip}', mac='{self.mac}')"
        )

    def summary(self) -> str:
        """Devuelve un resumen legible del dispositivo."""
        return f"[{self.__class__.__name__}] {self.hostname} | {self.ip} | Dept: {self.department}"


class Router(NetworkDevice):
    """
    Representa un router o dispositivo de capa 3.
    Incluye atributos específicos como el modelo y las VLANs configuradas.
    """

    def __init__(
        self,
        hostname: str,
        ip: str,
        mac: str,
        department: str = "Networking",
        model: str = "Desconocido",
        vlans: list[int] | None = None,
        firmware_version: str = "N/A",
    ) -> None:
        super().__init__(hostname, ip, mac, department)
        self.model: str = model
        self.vlans: list[int] = vlans or []
        self.firmware_version: str = firmware_version

    def audit_device(self) -> None:
        print(f"\n  🔀 AUDITORÍA DE ROUTER: {self.hostname} ({self.ip})")
        print("  " + "─" * 50)
        checks = [
            ("🔒", "Cambiar credenciales por defecto (admin/admin)"),
            ("🛡️", "Deshabilitar acceso HTTP, usar HTTPS o SSH únicamente"),
            ("📋", f"Revisar ACLs para las VLANs: {self.vlans or 'ninguna configurada'}"),
            ("🔄", f"Actualizar firmware (versión actual: {self.firmware_version})"),
            ("📡", "Deshabilitar protocolos no usados (Telnet, SNMP v1/v2)"),
            ("📝", "Habilitar logging centralizado (syslog)"),
        ]
        for icon, check in checks:
            print(f"  {icon} {check}")


class Server(NetworkDevice):
    """
    Representa un servidor físico o virtual.
    Incluye atributos como SO, RAM y si tiene servicios expuestos.
    """

    def __init__(
        self,
        hostname: str,
        ip: str,
        mac: str,
        department: str = "Sistemas",
        os_name: str = "Linux",
        ram_gb: int = 8,
        open_ports: list[int] | None = None,
        last_patch: str = "Desconocida",
    ) -> None:
        super().__init__(hostname, ip, mac, department)
        self.os_name: str = os_name
        self.ram_gb: int = ram_gb
        self.open_ports: list[int] = open_ports or []
        self.last_patch: str = last_patch

    def audit_device(self) -> None:
        print(f"\n  🖥️  AUDITORÍA DE SERVIDOR: {self.hostname} ({self.ip})")
        print("  " + "─" * 50)
        checks = [
            ("🔐", "Deshabilitar login root por SSH, usar usuarios no privilegiados"),
            ("🔑", "Implementar autenticación por clave pública (SSH keys)"),
            ("🚪", f"Revisar puertos abiertos: {self.open_ports or 'no especificados'}"),
            ("📦", f"Aplicar parches de seguridad (último: {self.last_patch})"),
            ("🛡️", "Configurar firewall (ufw/iptables) y fail2ban"),
            ("📊", f"RAM disponible: {self.ram_gb} GB — verificar recursos"),
        ]

        # Advertencia extra si el SO es Windows Server (más atacado)
        if "windows" in self.os_name.lower():
            checks.append(("⚠️", "Revisar políticas de Windows Defender y RDP"))
            checks.append(("🔄", "Verificar Windows Update y WSUS"))

        # Advertencia si tiene RAM baja
        if self.ram_gb < 4:
            checks.insert(0, ("🚨", f"RAM MUY BAJA ({self.ram_gb} GB) — riesgo de OOM"))

        for icon, check in checks:
            print(f"  {icon} {check}")


class Switch(NetworkDevice):
    """
    Representa un switch de capa 2.
    """

    def __init__(
        self,
        hostname: str,
        ip: str,
        mac: str,
        department: str = "Networking",
        port_count: int = 24,
        managed: bool = True,
    ) -> None:
        super().__init__(hostname, ip, mac, department)
        self.port_count: int = port_count
        self.managed: bool = managed

    def audit_device(self) -> None:
        print(f"\n  🔌 AUDITORÍA DE SWITCH: {self.hostname} ({self.ip})")
        print("  " + "─" * 50)
        checks = [
            ("🔒", "Asegurar que el acceso de gestión solo es desde VLAN admin"),
            ("🚫", "Deshabilitar puertos no usados"),
            ("🛡️", "Activar Port Security y 802.1X si es switch managed"),
            ("📋", "Documentar la asignación de puertos a VLANs"),
        ]
        if not self.managed:
            checks.insert(0, ("⚠️", "Switch NO gestionado — considerar reemplazar"))
        for icon, check in checks:
            print(f"  {icon} {check}")
