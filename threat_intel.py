#!/usr/bin/env python3
"""
threat_intel.py - Integración con API de inteligencia de amenazas (ipinfo.io).
Geolocaliza IPs sospechosas extraídas del auth.log.
"""

import requests


_API_BASE_URL = "https://ipinfo.io"
_TIMEOUT_SECONDS = 5


def geolocate_ip(ip: str) -> dict[str, str]:
    """
    Consulta ipinfo.io para obtener información geográfica y de organización de una IP.

    Args:
        ip: Dirección IP a consultar.

    Returns:
        Diccionario con claves: ip, country, org, city, region.

    Raises:
        requests.RequestException: Si la solicitud HTTP falla.
    """
    url = f"{_API_BASE_URL}/{ip}/json"

    try:
        response = requests.get(url, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        data: dict = response.json()

        return {
            "ip": data.get("ip", ip),
            "country": data.get("country", "??"),
            "city": data.get("city", "Desconocida"),
            "region": data.get("region", ""),
            "org": data.get("org", "Organización desconocida"),
        }
    except requests.Timeout:
        return {
            "ip": ip,
            "country": "TIMEOUT",
            "city": "-",
            "region": "-",
            "org": "Tiempo de espera agotado",
        }
    except requests.ConnectionError:
        return {
            "ip": ip,
            "country": "ERROR",
            "city": "-",
            "region": "-",
            "org": "Sin conexión a la API",
        }
    except requests.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        return {
            "ip": ip,
            "country": "ERROR",
            "city": "-",
            "region": "-",
            "org": f"HTTP {code}",
        }

def enrich_ips_table(ip_counts: dict[str, int]) -> list[dict[str, str | int]]:
    """
    Enriquece una lista de IPs con su geolocalización y muestra una tabla por consola.

    Args:
        ip_counts: Diccionario {ip: número_de_intentos_fallidos}.

    Returns:
        Lista de diccionarios con información completa por IP.
    """
    print("\n  🌍 Consultando threat intelligence para las IPs más agresivas...\n")

    results: list[dict[str, str | int]] = []

    col_ip = 18
    col_attempts = 10
    col_country = 8
    col_city = 16
    col_org = 30

    header = (
        f"  {'IP':<{col_ip}} {'Intentos':>{col_attempts}}  "
        f"{'País':<{col_country}} {'Ciudad':<{col_city}} {'Organización':<{col_org}}"
    )
    separator = "  " + "─" * (col_ip + col_attempts + col_country + col_city + col_org + 6)

    print(header)
    print(separator)

    for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True):
        info = geolocate_ip(ip)
        row: dict[str, str | int] = {
            "ip": ip,
            "attempts": count,
            "country": info["country"],
            "city": info["city"],
            "org": info["org"],
        }
        results.append(row)

        org_short = info["org"][:col_org]
        print(
            f"  {ip:<{col_ip}} {count:>{col_attempts}}  "
            f"{info['country']:<{col_country}} {info['city']:<{col_city}} {org_short:<{col_org}}"
        )

    print(separator)
    print(f"\n  ✅ {len(results)} IPs enriquecidas con datos de geolocalización.")
    return results
