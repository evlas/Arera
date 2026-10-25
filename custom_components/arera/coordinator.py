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
    OFFICIAL_ARERA_XLSX_URL,
    SOURCE_TYPE_MANUAL,
)
from .parser import parse_arera_xlsx

_LOGGER = logging.getLogger(__name__)


class AreraDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator per gestire l'acquisizione dei dati ARERA."""

    def __init__(self, hass: HomeAssistant, config_entry) -> None:
        """Inizializza il coordinator."""
        self.entry = config_entry
        self.source_type = config_entry.data.get(CONF_SOURCE_TYPE, "arera_xlsx")
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
        """Recupera i dati da ARERA o usa i dati di fallback/configurati."""
        data: dict[str, Any] = dict(DEFAULT_ARERA_VALUES)
        data["today"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Se sono presenti override nelle options
        for key in DEFAULT_ARERA_VALUES:
            if key in self.entry.options:
                try:
                    data[key] = float(self.entry.options[key])
                except (ValueError, TypeError):
                    pass

        # Se la modalità non è manuale ed è presente un URL, tenta il download
        if self.source_type != SOURCE_TYPE_MANUAL and self.url:
            try:
                session = async_get_clientsession(self.hass)
                # Imposta header User-Agent per compatibilità arera.it
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                async with async_timeout.timeout(30):
                    async with session.get(self.url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.read()
                            # Verifica se è un file zip/xlsx (magic number PK\x03\x04)
                            if content.startswith(b"PK\x03\x04") or ".xlsx" in self.url.lower():
                                _LOGGER.debug("File Excel ARERA ricevuto (%d byte), avvio parsing...", len(content))
                                parsed = parse_arera_xlsx(content)
                                data.update(parsed)
                            else:
                                # Prova come JSON
                                try:
                                    import json
                                    json_data = json.loads(content.decode("utf-8", errors="ignore"))
                                    if isinstance(json_data, dict):
                                        _LOGGER.debug("Dati JSON ARERA ricevuti con successo: %s", json_data)
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
                                    _LOGGER.warning("Risposta ARERA non riconosciuta come Excel né JSON: %s", json_err)
                        else:
                            _LOGGER.warning(
                                "Errore HTTP %s recuperando i dati ARERA da %s. Vengono usati i valori di fallback.",
                                response.status,
                                self.url,
                            )
            except Exception as err:
                _LOGGER.warning(
                    "Impossibile contattare la sorgente ARERA %s (%s). Vengono utilizzati i valori predefiniti.",
                    self.url,
                    err,
                )

        return data
