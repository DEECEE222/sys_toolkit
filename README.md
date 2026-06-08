# SYS TOOLKIT v1.0 — ASIR Fase 7

Kit de herramientas para administradores de sistemas desarrollado en Python. Automatiza auditorías de seguridad SSH, análisis de inventarios de red, inteligencia de amenazas y generación de informes ejecutivos en Excel.

---

## Requisitos

- Python 3.10 o superior
- Windows, Linux o macOS

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/DEECEE222/sys_toolkit.git
cd sys_toolkit

# 2. Crear el entorno virtual
python -m venv venv

# 3. Activar el entorno virtual
source venv/Scripts/activate   # Windows
source venv/bin/activate       # Linux / macOS

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Generar los datos de prueba
python generate_inventory.py
```

---

## Uso

```bash
python sys_toolkit.py
```

Se abre un menú interactivo con 6 herramientas:

| Opción | Herramienta | Descripción |
|--------|-------------|-------------|
| 1 | Ping | Comprueba si una IP responde en la red |
| 2 | Disco | Verifica el espacio libre de una partición y alerta si baja del 20% |
| 3 | Auditoria SSH | Analiza `auth.log` y muestra las IPs con más intentos de login fallidos |
| 4 | Threat Intelligence | Geolocaliza las IPs atacantes consultando la API de ipinfo.io |
| 5 | Inventario | Carga el CSV con Pandas y filtra servidores Windows, RAM baja y vulnerables |
| 6 | Informe Excel | Genera un `.xlsx` ejecutivo con 5 hojas y formato profesional |

---

## Estructura del proyecto

```
sys_toolkit/
├── sys_toolkit.py          # Menu CLI principal
├── os_utils.py             # Ping y comprobacion de disco
├── log_parser.py           # Parseo de auth.log
├── network_models.py       # POO: Router, Server, Switch
├── threat_intel.py         # Integracion con API ipinfo.io
├── generate_inventory.py   # Generador de datos de prueba
├── inventory_manager.py    # Analisis de inventario con Pandas
├── report_generator.py     # Generacion de informes Excel
├── scheduler.py            # Demonio de automatizacion
├── requirements.txt
├── .gitignore
├── data/
│   ├── inventory.csv       # 1000 servidores ficticios
│   └── auth.log            # Log SSH simulado con ataques
├── reports/
│   └── informe.xlsx        # Informe ejecutivo generado
├── docs/
│   └── python-sysadmin.md  # Documentacion tecnica
└── tests/
    └── test_toolkit.py     # 24 tests unitarios
```

---

## Tests

```bash
pytest tests/ -v
```

```
24 passed in Xs
```

Los tests cubren tres modulos:

- **TestLogParser** — verifica que el parseo de IPs, la deduplicacion con Set y el conteo de intentos son correctos
- **TestOsUtils** — verifica ping a localhost y comprobacion de disco
- **TestNetworkModels** — verifica creacion de dispositivos, polimorfismo y auditorias especificas por tipo

---

## Verificacion de tipos

```bash
mypy sys_toolkit.py os_utils.py log_parser.py network_models.py threat_intel.py
```

```
Success: no issues found in 5 source files
```

---

## Scheduler (demonio)

Automatiza las tareas principales en segundo plano:

```bash
python scheduler.py
```

| Tarea | Frecuencia |
|-------|------------|
| Informe Excel | Cada 30 dias |
| Comprobacion de disco | Cada hora |
| Analisis de logs SSH | Cada hora |

Los resultados se guardan en `logs/scheduler.log`. Para detenerlo: **Ctrl+C**

---

## Tecnologias

`Python 3` · `Pandas` · `OpenPyXL` · `Requests` · `Faker` · `pytest` · `mypy` · `schedule` · `subprocess`
