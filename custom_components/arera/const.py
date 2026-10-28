"""Costanti per l'integrazione ARERA Tariffe Luce."""
from datetime import datetime

DOMAIN = "arera"

CONF_SOURCE_TYPE = "source_type"
CONF_URL = "url"
CONF_SCAN_INTERVAL = "scan_interval"

SOURCE_TYPE_ARERA_XLSX = "arera_xlsx"
SOURCE_TYPE_CUSTOM_URL = "custom_url"
SOURCE_TYPE_MANUAL = "manual"


def get_arera_stg_urls(year: int | None = None) -> list[str]:
    """Restituisce la lista ordinata di URL ufficiali ARERA per il file STG con fallback."""
    if year is None:
        year = datetime.now().year
    return [
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{year}_stg_domesticiNonVulnerabili.xlsx",
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{year - 1}_stg_domesticiNonVulnerabili.xlsx",
        "https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/stg_domesticiNonVulnerabili.xlsx",
    ]


def get_arera_smt_urls(year: int | None = None) -> list[str]:
    """Restituisce la lista ordinata di URL ufficiali ARERA per il file SMT con fallback."""
    if year is None:
        year = datetime.now().year
    return [
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{year}-smt.xlsx",
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{year - 1}-smt.xlsx",
        "https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E2026-smt.xlsx",
    ]


# URL predefiniti (anno corrente)
OFFICIAL_ARERA_XLSX_URL = get_arera_stg_urls()[0]
DEFAULT_URL = OFFICIAL_ARERA_XLSX_URL
OFFICIAL_ARERA_SMT_XLSX_URL = get_arera_smt_urls()[0]
OFFICIAL_ARERA_SMT_FALLBACK_URL = get_arera_smt_urls()[1]

DEFAULT_SCAN_INTERVAL_HOURS = 24

# Valori di fallback ARERA (estratti dalle tabelle ufficiali ARERA per clienti domestici residenti BT)
DEFAULT_ARERA_VALUES = {
    "s1": 23.04,            # Quota Fissa Trasporto e Misura (€/anno)
    "s2": 23.52,            # Quota Potenza Trasporto e Misura (€/kW/anno)
    "s3": 0.0119,           # Quota Energia Trasporto e Misura (€/kWh)
    "uc3": 0.00276,         # UC3 Perequazione (€/kWh)
    "uc6qe": 0.00007,       # UC6 Quota Energia (€/kWh)
    "uc6qp": 0.1988,        # UC6 Quota Potenza (€/kW/anno)
    "asos": 0.031515,       # ASOS Rinnovabili (€/kWh) - Settembre 2026
    "arim": 0.001638,       # ARIM Altri Oneri (€/kWh)
    "dispbt": 1.107,        # DispBT (€/anno) - Delibera ARERA 218/2026/R/eel
    "cdispd": 0.015068,     # CDISPD (€/kWh)
    "csed": 0.00056,        # CSED (€/kWh)
    "cpstgd": 0.00208,      # CPSTGD (€/kWh)
    "parametrolamda": -73.5737,  # Parametro gamma/lambda STG (€/anno)
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
