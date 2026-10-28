"""Costanti per l'integrazione ARERA Tariffe Luce e Gas."""
from datetime import datetime

DOMAIN = "arera"

CONF_SERVICE_TYPE = "service_type"
CONF_SOURCE_TYPE = "source_type"
CONF_URL = "url"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_GAS_AMBITO = "gas_ambito"
CONF_GAS_SCAGLIONE = "gas_scaglione"

SERVICE_TYPE_ELECTRICITY = "electricity"
SERVICE_TYPE_GAS = "gas"
SERVICE_TYPE_BOTH = "both"

SOURCE_TYPE_ARERA_XLSX = "arera_xlsx"
SOURCE_TYPE_CUSTOM_URL = "custom_url"
SOURCE_TYPE_MANUAL = "manual"

# Ambiti geografici per la distribuzione del gas naturale
GAS_AMBITI = {
    "nord_occidentale": "Nord Occidentale (Piemonte, Valle d'Aosta, Liguria)",
    "nord_orientale": "Nord Orientale (Lombardia, Veneto, Trentino-A.A., Friuli-V.G., Emilia-Romagna)",
    "centrale": "Centrale (Toscana, Umbria, Marche)",
    "centro_sud_orientale": "Centro-Sud Orientale (Abruzzo, Molise, Puglia, Basilicata)",
    "centro_sud_occidentale": "Centro-Sud Occidentale (Lazio, Campania)",
    "meridionale": "Meridionale (Calabria, Sicilia)",
    "sardegna": "Sardegna",
}
DEFAULT_GAS_AMBITO = "nord_orientale"

# Scaglioni di consumo annuo per il gas naturale
GAS_SCAGLIONI = {
    "scaglione_1": "Scaglione 1: da 0 a 120 Smc/anno (cottura)",
    "scaglione_2": "Scaglione 2: da 121 a 480 Smc/anno (cottura + acqua calda)",
    "scaglione_3": "Scaglione 3: da 481 a 1.560 Smc/anno (riscaldamento autonomo)",
    "scaglione_4": "Scaglione 4: da 1.561 a 5.000 Smc/anno (bifamiliare / consumi elevati)",
}
DEFAULT_GAS_SCAGLIONE = "scaglione_3"


def get_arera_stg_urls(year: int | None = None) -> list[str]:
    """Restituisce la lista ordinata di URL ufficiali ARERA per il file STG Luce con fallback."""
    if year is None:
        year = datetime.now().year
    return [
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{year}_stg_domesticiNonVulnerabili.xlsx",
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{year - 1}_stg_domesticiNonVulnerabili.xlsx",
        "https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/stg_domesticiNonVulnerabili.xlsx",
    ]


def get_arera_smt_urls(year: int | None = None) -> list[str]:
    """Restituisce la lista ordinata di URL ufficiali ARERA per il file SMT Luce con fallback."""
    if year is None:
        year = datetime.now().year
    return [
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{year}-smt.xlsx",
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E{year - 1}-smt.xlsx",
        "https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/E2026-smt.xlsx",
    ]


def get_arera_gas_urls(year: int | None = None) -> list[str]:
    """Restituisce la lista ordinata di URL ufficiali ARERA per il file STV Gas con fallback."""
    if year is None:
        year = datetime.now().year
    return [
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/G{year}_stv.xlsx",
        f"https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/G{year - 1}_stv.xlsx",
    ]


# URL predefiniti (anno corrente)
OFFICIAL_ARERA_XLSX_URL = get_arera_stg_urls()[0]
DEFAULT_URL = OFFICIAL_ARERA_XLSX_URL
OFFICIAL_ARERA_SMT_XLSX_URL = get_arera_smt_urls()[0]
OFFICIAL_ARERA_SMT_FALLBACK_URL = get_arera_smt_urls()[1]
OFFICIAL_ARERA_GAS_URL = get_arera_gas_urls()[0]

DEFAULT_SCAN_INTERVAL_HOURS = 24

# Valori di fallback ARERA Energia Elettrica (domestici residenti BT)
DEFAULT_ARERA_VALUES = {
    "s1": 23.04,            # Quota Fissa Trasporto e Misura (€/anno)
    "s2": 23.52,            # Quota Potenza Trasporto e Misura (€/kW/anno)
    "s3": 0.0119,           # Quota Energia Trasporto e Misura (€/kWh)
    "uc3": 0.00276,         # UC3 Perequazione (€/kWh)
    "uc6qe": 0.00007,       # UC6 Quota Energia (€/kWh)
    "uc6qp": 0.1988,        # UC6 Quota Potenza (€/kW/anno)
    "asos": 0.031515,       # ASOS Rinnovabili (€/kWh)
    "arim": 0.001638,       # ARIM Altri Oneri (€/kWh)
    "dispbt": 1.107,        # DispBT (€/anno)
    "cdispd": 0.015068,     # CDISPD (€/kWh)
    "csed": 0.00056,        # CSED (€/kWh)
    "cpstgd": 0.00208,      # CPSTGD (€/kWh)
    "parametrolamda": -73.5737,  # Parametro lambda STG (€/anno)
}

# Valori di fallback ARERA Gas Naturale (Nord Orientale, scaglione 3)
DEFAULT_ARERA_GAS_VALUES = {
    "gas_cmemm": 0.843182,      # Materia prima gas (€/Smc)
    "gas_ccr": 0.03151,         # Approvvigionamento (€/Smc)
    "gas_qvd_variabile": 0.007946,  # Vendita al dettaglio quota variabile (€/Smc)
    "gas_tau3": 0.072643,       # Trasporto e misura variabile (€/Smc)
    "gas_qt": 0.074395,         # Trasporto (€/Smc)
    "gas_rs": 0.002788,         # Qualità del servizio (€/Smc)
    "gas_ug1": 0.034837,        # Perequazione (€/Smc)
    "gas_re": 0.029417,         # Risparmio energetico (€/Smc)
    "gas_ug2_variabile": 0.0293,  # Oneri commercializzazione variabile (€/Smc)
    "gas_ug3": 0.007292,        # Recupero morosità (€/Smc)
    "gas_totale_variabile": 1.13331,  # Totale spesa variabile al metro cubo (€/Smc)
    "gas_qvd_fissa": 55.39,     # Vendita quota fissa (€/anno)
    "gas_tau1": 69.60,          # Distribuzione quota fissa contatore G6 (€/anno)
    "gas_ug2_fissa": -21.63,    # Compensazione quota fissa (€/anno)
    "gas_totale_fissa": 103.00, # Totale spesa fissa annua (€/anno)
}

# Metadata sensori Energia Elettrica
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

# Metadata sensori Gas Naturale
GAS_SENSOR_TYPES = {
    "gas_cmemm": {
        "unit": "€/Smc",
        "icon": "mdi:fire",
    },
    "gas_ccr": {
        "unit": "€/Smc",
        "icon": "mdi:gas-burner",
    },
    "gas_qvd_variabile": {
        "unit": "€/Smc",
        "icon": "mdi:cash-multiple",
    },
    "gas_tau3": {
        "unit": "€/Smc",
        "icon": "mdi:pipe",
    },
    "gas_qt": {
        "unit": "€/Smc",
        "icon": "mdi:truck-delivery",
    },
    "gas_rs": {
        "unit": "€/Smc",
        "icon": "mdi:seal",
    },
    "gas_ug1": {
        "unit": "€/Smc",
        "icon": "mdi:scale-balance",
    },
    "gas_re": {
        "unit": "€/Smc",
        "icon": "mdi:leaf",
    },
    "gas_ug2_variabile": {
        "unit": "€/Smc",
        "icon": "mdi:scale-balance",
    },
    "gas_ug3": {
        "unit": "€/Smc",
        "icon": "mdi:scale-balance",
    },
    "gas_totale_variabile": {
        "unit": "€/Smc",
        "icon": "mdi:calculator",
    },
    "gas_qvd_fissa": {
        "unit": "€/anno",
        "icon": "mdi:currency-eur",
    },
    "gas_tau1": {
        "unit": "€/anno",
        "icon": "mdi:counter",
    },
    "gas_ug2_fissa": {
        "unit": "€/anno",
        "icon": "mdi:scale-balance",
    },
    "gas_totale_fissa": {
        "unit": "€/anno",
        "icon": "mdi:calculator",
    },
    "gas_periodo": {
        "unit": None,
        "icon": "mdi:calendar-clock",
    },
}
