# Python para Administradores de Sistemas (ASIR) — Guía técnica

## ¿Por qué Python además de Bash?

Bash es insustituible para tareas rápidas del SO: mover archivos, encadenar comandos, scripts de arranque. Pero tiene límites claros en cuanto la complejidad crece:

| Aspecto | Bash | Python |
|---|---|---|
| Parseo de texto simple | ✅ Ideal | Posible pero verboso |
| Estructuras de datos (dict, set) | ❌ Muy limitado | ✅ Nativo y potente |
| Consumir APIs REST / JSON | ❌ Frágil con curl+jq | ✅ `requests` + `.json()` |
| Análisis de datos masivos (CSV, Excel) | ❌ Imposible | ✅ Pandas + OpenPyXL |
| Testing automatizado | ❌ Sin framework | ✅ pytest |
| Orientación a objetos | ❌ No existe | ✅ Clases, herencia, polimorfismo |
| Legibilidad en proyectos grandes | ❌ Se vuelve ilegible | ✅ Type hints, módulos |

---

## Módulos del toolkit

### `sys_toolkit.py` — Menú principal CLI
Punto de entrada con menú interactivo. Demuestra type hints estrictos y despacho de funciones con diccionario en lugar de `if/elif` anidados.

### `os_utils.py` — Automatización del SO
- **`check_ping(ip)`** — Llama a `ping -c 1` vía `subprocess.run()`. Devuelve `bool`. Captura `TimeoutExpired` para no bloquear el proceso.
- **`check_disk_space(path, threshold_pct)`** — Usa `shutil.disk_usage()` para leer el uso real. Emite alerta si el espacio libre baja del umbral.

### `log_parser.py` — Parseo de auth.log
Usa el gestor de contexto `with open(...)` para leer el archivo línea a línea **sin cargar todo en RAM** (crítico en logs de producción de varios GB). Extrae IPs con regex, las acumula en un `set` (deduplicación O(1)) y cuenta intentos con un `dict`.

### `network_models.py` — POO para inventario de red
Demuestra los tres pilares de la POO:
- **Encapsulación**: cada clase agrupa atributos relevantes (hostname, IP, MAC + específicos).
- **Herencia**: `Router`, `Server` y `Switch` heredan de `NetworkDevice`.
- **Polimorfismo**: `audit_device()` tiene comportamiento diferente en cada subclase. El código cliente no necesita saber el tipo concreto.

### `threat_intel.py` — Integración con API
Consulta `ipinfo.io` para geolocalizar IPs atacantes. Usa `requests.get()` con `timeout` y captura `requests.Timeout`, `requests.ConnectionError` y `requests.HTTPError` por separado para dar mensajes útiles en cada caso.

### `generate_inventory.py` — Generación de datos de prueba
Usa `faker` para nombres y emails realistas, `random` con semilla fija (reproducibilidad) y el módulo `csv` para escritura eficiente de 1000+ filas.

### `inventory_manager.py` — Análisis con Pandas
Demuestra:
- Filtrado con máscaras booleanas (`df[mask]`)
- `str.contains()` para búsqueda en columnas de texto
- `groupby().agg()` para estadísticas por departamento
- `pd.to_datetime()` + `pd.Timedelta` para filtrar por fechas

### `report_generator.py` — Informes Excel con OpenPyXL
Genera un `.xlsx` con 5 hojas, cabeceras con color corporativo, filas alternadas, columnas ajustadas automáticamente y panel superior congelado. Listo para enviar a gerencia.

### `tests/test_toolkit.py` — Tests unitarios con pytest
24 tests organizados en 3 clases. Usa `tmp_path` (fixture de pytest) para crear archivos temporales sin ensuciar el sistema de archivos.

---

## Ejecución

```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Generar datos de prueba
python generate_inventory.py

# 3. Lanzar el toolkit interactivo
python sys_toolkit.py

# 4. Ejecutar tests
pytest tests/ -v

# 5. Verificar tipos estáticos
mypy sys_toolkit.py os_utils.py log_parser.py network_models.py
```

---

## Automatización mensual (schedule)

El módulo `schedule` permite ejecutar el informe automáticamente:

```python
import schedule, time
from report_generator import generate_excel_report

def job():
    generate_excel_report("data/inventory.csv", "reports/informe_mensual.xlsx")

schedule.every().month.do(job)
while True:
    schedule.run_pending()
    time.sleep(3600)
```
