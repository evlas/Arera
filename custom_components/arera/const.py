"""Costanti per l'integrazione ARERA Tariffe Luce."""
from datetime import datetime

DOMAIN = "arera"

CONF_SOURCE_TYPE = "source_type"
CONF_URL = "url"
CONF_SCAN_INTERVAL = "scan_interval"

SOURCE_TYPE_ARERA_XLSX = "arera_xlsx"
SOURCE_TYPE_CUSTOM_URL = "custom_url"
SOURCE_TYPE_MANUAL = "manual"

# File ufficiali ARERA scaricati direttamente dalla rete
OFFICIAL_ARERA_XLSX_URL = "https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/stg_domesticiNonVulnerabili.xlsx"
OFFICIAL_ARERA_SMT_XLSX_URL = f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{datetime.now().year}-smt.xlsx"
OFFICIAL_ARERA_SMT_FALLBACK_URL = "https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E2026-smt.xlsx"

DEFAULT_URL = OFFICIAL_ARERA_XLSX_URL
DEFAULT_SCAN_INTERVAL_HOURS = 24

# Valori di fallback ARERA (estratti dalle tabelle ufficiali ARERA per clienti domestici residenti BT)
DEFAULT_ARERA_VALUES = {
    "s1": 23.04,            # Quota Fissa Trasporto e Misura (€/anno)
    "s2": 23.52,            # Quota Potenza Trasporto e Misura (€/kW/anno)
    "s3": 0.0119,           # Quota Energia Trasporto e Misura (€/kWh)
    "uc3": 0.00276,         # UC3 Perequazione (€/kWh)
    "uc6qe": 0.00007,       # UC6 Quota Energia (€/kWh)
    "uc6qp": 0.1988,        # UC6 Quota Potenza (€/kW/anno)
    "asos": 0.028657,       # ASOS Rinnovabili (€/kWh)
    "arim": 0.001638,       # ARIM Altri Oneri (€/kWh)
    "dispbt": 1.107,        # DispBT (€/anno) - Delibera ARERA 218/2026/R/eel (estratta live da E2026-smt.xlsx)
    "cdispd": 0.019902,     # CDISPD (€/kWh)
    "csed": 0.00056,        # CSED (€/kWh)
    "cpstgd": 0.00214,      # CPSTGD (€/kWh)
    "parametrolamda": -73.1637,  # Parametro gamma/lambda STG (€/anno)
}

SENSOR_TYPES = {
    "s1": {
        "unit": "€/anno",
        "icon": "mdi:currency-eur",
    },
    "s2": {
        "unit": "€/kW/anno",
        "icon": "mdi:flash",
    },
    "s3": {
        "unit": "€/kWh",
        "icon": "mdi:transmission-tower",
    },
    "uc3": {
        "unit": "€/kWh",
        "icon": "mdi:scale-balance",
    },
    "uc6qe": {
        "unit": "€/kWh",
        "icon": "mdi:scale-balance",
    },
    "uc6qp": {
        "unit": "€/kW/anno",
        "icon": "mdi:scale-balance",
    },
    "asos": {
        "unit": "€/kWh",
        "icon": "mdi:solar-power",
    },
    "arim": {
        "unit": "€/kWh",
        "icon": "mdi:chart-timeline-variant",
    },
    "dispbt": {
        "unit": "€/anno",
        "icon": "mdi:transmission-tower-export",
    },
    "cdispd": {
        "unit": "€/kWh",
        "icon": "mdi:transmission-tower",
    },
    "csed": {
        "unit": "€/kWh",
        "icon": "mdi:scale-balance",
    },
    "cpstgd": {
        "unit": "€/kWh",
        "icon": "mdi:scale-balance",
    },
    "parametrolamda": {
        "unit": "€/anno",
        "icon": "mdi:lambda",
    },
    "today": {
        "unit": None,
        "icon": "mdi:calendar-clock",
    },
}
