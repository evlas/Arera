"""Costanti per l'integrazione ARERA Tariffe Luce."""

DOMAIN = "arera"

CONF_SOURCE_TYPE = "source_type"
CONF_URL = "url"
CONF_SCAN_INTERVAL = "scan_interval"

SOURCE_TYPE_URL = "url"
SOURCE_TYPE_MANUAL = "manual"

DEFAULT_URL = "http://192.168.70.50/arera/arera.json"
DEFAULT_SCAN_INTERVAL_HOURS = 24

# Valori di default ARERA (aggiornati per clienti domestici BT)
DEFAULT_ARERA_VALUES = {
    "s1": 24.40,            # Quota Fissa (€/anno)
    "s2": 23.50,            # Quota Potenza (€/kW/anno)
    "s3": 0.0135,           # Quota Energia (€/kWh)
    "uc3": 0.0016,          # UC3 (€/kWh)
    "uc6qe": 0.0001,        # UC6 Quota Energia (€/kWh)
    "uc6qp": 0.0000,        # UC6 Quota Potenza (€/kW/anno)
    "asos": 0.0345,         # Asos (€/kWh)
    "arim": 0.0090,         # Arim (€/kWh)
    "dispbt": -10.77,       # DispBT (€/anno)
    "cdispd": 0.0018,       # CDISPD (€/kWh)
    "csed": 0.0010,         # CSED (€/kWh)
    "cpstgd": 0.0000,       # CPSTGD (€/kWh)
    "parametrolamda": 0.0,  # Parametro lambda (€/anno)
}

SENSOR_TYPES = {
    "s1": {
        "name": "Arera Quota Fissa",
        "entity_id": "sensor.arera_quota_fissa",
        "unit": "€/anno",
        "icon": "mdi:currency-eur",
    },
    "s2": {
        "name": "Arera Quota Potenza",
        "entity_id": "sensor.arera_quota_potenza",
        "unit": "€/kW/anno",
        "icon": "mdi:flash",
    },
    "s3": {
        "name": "Arera Quota Energia",
        "entity_id": "sensor.arera_quota_energia",
        "unit": "€/kWh",
        "icon": "mdi:transmission-tower",
    },
    "uc3": {
        "name": "Arera UC3",
        "entity_id": "sensor.arera_uc3",
        "unit": "€/kWh",
        "icon": "mdi:scale-balance",
    },
    "uc6qe": {
        "name": "Arera UC6 QE",
        "entity_id": "sensor.arera_uc6_qe",
        "unit": "€/kWh",
        "icon": "mdi:scale-balance",
    },
    "uc6qp": {
        "name": "Arera UC6 QP",
        "entity_id": "sensor.arera_uc6_qp",
        "unit": "€/kW/anno",
        "icon": "mdi:scale-balance",
    },
    "asos": {
        "name": "Arera Asos",
        "entity_id": "sensor.arera_asos",
        "unit": "€/kWh",
        "icon": "mdi:solar-power",
    },
    "arim": {
        "name": "Arera Arim",
        "entity_id": "sensor.arera_arim",
        "unit": "€/kWh",
        "icon": "mdi:chart-timeline-variant",
    },
    "dispbt": {
        "name": "Arera DispBT",
        "entity_id": "sensor.arera_dispbt",
        "unit": "€/anno",
        "icon": "mdi:transmission-tower-export",
    },
    "cdispd": {
        "name": "Arera CDISPD",
        "entity_id": "sensor.arera_cdispd",
        "unit": "€/kWh",
        "icon": "mdi:transmission-tower",
    },
    "csed": {
        "name": "Arera CSED",
        "entity_id": "sensor.arera_csed",
        "unit": "€/kWh",
        "icon": "mdi:scale-balance",
    },
    "cpstgd": {
        "name": "Arera CPSTGD",
        "entity_id": "sensor.arera_cpstgd",
        "unit": "€/kWh",
        "icon": "mdi:scale-balance",
    },
    "parametrolamda": {
        "name": "Arera Parametro lamda",
        "entity_id": "sensor.arera_parametro_lamda",
        "unit": "€/anno",
        "icon": "mdi:lambda",
    },
    "today": {
        "name": "Arera Ultimo Aggiornamento",
        "entity_id": "sensor.arera_ultimo_aggiornamento",
        "unit": None,
        "icon": "mdi:calendar-clock",
    },
}
