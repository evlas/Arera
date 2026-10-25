"""DataUpdateCoordinator per ARERA Tariffe."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SOURCE_TYPE,
    CONF_URL,
    DEFAULT_ARERA_VALUES,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DEFAULT_URL,
    DOMAIN,
    OFFICIAL_ARERA_SMT_FALLBACK_URL,
    OFFICIAL_ARERA_SMT_XLSX_URL,
    OFFICIAL_ARERA_XLSX_URL,
    SOURCE_TYPE_ARERA_XLSX,
    SOURCE_TYPE_MANUAL,
)
from .parser import parse_arera_smt_xlsx, parse_arera_xlsx

_LOGGER = logging.getLogger(__name__)


class AreraDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator per gestire l'acquisizione dei dati ARERA dalla rete."""

    def __init__(self, hass: HomeAssistant, config_entry) -> None:
        """Inizializza il coordinator."""
        self.entry = config_entry
        self.source_type = config_entry.data.get(CONF_SOURCE_TYPE, SOURCE_TYPE_ARERA_XLSX)
        self.url = config_entry.options.get(
            CONF_URL, config_entry.data.get(CONF_URL, DEFAULT_URL)
        )
        scan_interval_hours = config_entry.options.get(
            "scan_interval",
            config_entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL_HOURS),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=scan_interval_hours),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Recupera i dati da ARERA via web o usa i dati di fallback."""
        data: dict[str, Any] = dict(DEFAULT_ARERA_VALUES)
        data["today"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Sovrascritture manuali se configurate
        for key in DEFAULT_ARERA_VALUES:
            if key in self.entry.options:
                try:
                    data[key] = float(self.entry.options[key])
                except (ValueError, TypeError):
                    pass

        # Se la sorgente è automatica via web
        if self.source_type != SOURCE_TYPE_MANUAL and self.url:
            session = async_get_clientsession(self.hass)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            # 1. Download file principale (STG o Custom URL)
            try:
                async with async_timeout.timeout(30):
                    async with session.get(self.url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.read()
                            if content.startswith(b"PK") or ".xlsx" in self.url.lower():
                                _LOGGER.debug("File Excel ARERA ricevuto (%d byte), avvio parsing...", len(content))
                                parsed = parse_arera_xlsx(content)
                                data.update(parsed)
                            else:
                                # Prova come JSON
                                try:
                                    import json
                                    json_data = json.loads(content.decode("utf-8", errors="ignore"))
                                    if isinstance(json_data, dict):
                                        for k, v in json_data.items():
                                            k_lower = k.lower().replace("_", "")
                                            for default_k in DEFAULT_ARERA_VALUES:
                                                if default_k.lower() == k_lower:
                                                    try:
                                                        data[default_k] = float(v)
                                                    except (ValueError, TypeError):
                                                        pass
                                            if k_lower in ("today", "data", "date", "aggiornamento"):
                                                data["today"] = str(v)
                                except Exception as json_err:
                                    _LOGGER.warning("Risposta ARERA non riconosciuta: %s", json_err)
                        else:
                            _LOGGER.warning(
                                "Errore HTTP %s scaricando le tariffe ARERA da %s",
                                response.status,
                                self.url,
                            )
            except Exception as err:
                _LOGGER.warning(
                    "Impossibile scaricare le tariffe ARERA da %s (%s). Vengono usati i valori di fallback.",
                    self.url,
                    err,
                )

            # 2. Se in modalità ufficiale ARERA, recupera dinamicamente DispBT dal file SMT
            if self.source_type == SOURCE_TYPE_ARERA_XLSX:
                smt_urls = [OFFICIAL_ARERA_SMT_XLSX_URL, OFFICIAL_ARERA_SMT_FALLBACK_URL]
                for smt_url in smt_urls:
                    try:
                        async with async_timeout.timeout(20):
                            async with session.get(smt_url, headers=headers) as smt_resp:
                                if smt_resp.status == 200:
                                    smt_content = await smt_resp.read()
                                    if smt_content.startswith(b"PK"):
                                        smt_data = parse_arera_smt_xlsx(smt_content)
                                        if "dispbt" in smt_data:
                                            data["dispbt"] = smt_data["dispbt"]
                                            _LOGGER.info(
                                                "DispBT recuperato dinamicamente dalla rete ARERA (%s): %s €/anno",
                                                smt_url,
                                                data["dispbt"],
                                            )
                                            break
                    except Exception as smt_err:
                        _LOGGER.debug("Tentativo download SMT %s non riuscito: %s", smt_url, smt_err)

        return data
