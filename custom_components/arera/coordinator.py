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
    DOMAIN,
    SOURCE_TYPE_URL,
)

_LOGGER = logging.getLogger(__name__)


class AreraDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator per gestire l'acquisizione dei dati ARERA."""

    def __init__(self, hass: HomeAssistant, config_entry) -> None:
        """Inizializza il coordinator."""
        self.entry = config_entry
        self.source_type = config_entry.data.get(CONF_SOURCE_TYPE, SOURCE_TYPE_URL)
        self.url = config_entry.data.get(CONF_URL, "")
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
        """Recupera i dati dal server o usa i dati di fallback/configurati."""
        data: dict[str, Any] = dict(DEFAULT_ARERA_VALUES)
        data["today"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Se sono presenti override nelle options
        for key in DEFAULT_ARERA_VALUES:
            if key in self.entry.options:
                try:
                    data[key] = float(self.entry.options[key])
                except (ValueError, TypeError):
                    pass

        # Se la modalità è URL, tenta la chiamata HTTP
        if self.source_type == SOURCE_TYPE_URL and self.url:
            try:
                session = async_get_clientsession(self.hass)
                async with async_timeout.timeout(15):
                    async with session.get(self.url) as response:
                        if response.status == 200:
                            json_data = await response.json(content_type=None)
                            if isinstance(json_data, dict):
                                _LOGGER.debug("Dati ARERA ricevuti con successo: %s", json_data)
                                for k, v in json_data.items():
                                    k_lower = k.lower().replace("_", "")
                                    # Normalizza chiavi comuni
                                    matched_key = None
                                    for default_k in DEFAULT_ARERA_VALUES:
                                        if default_k.lower() == k_lower:
                                            matched_key = default_k
                                            break
                                    if matched_key:
                                        try:
                                            data[matched_key] = float(v)
                                        except (ValueError, TypeError):
                                            pass
                                    elif k_lower in ("today", "data", "date", "aggiornamento"):
                                        data["today"] = str(v)
                            else:
                                _LOGGER.warning("Risposta ARERA non è un JSON valido: %s", json_data)
                        else:
                            _LOGGER.warning(
                                "Errore HTTP %s recuperando i dati ARERA da %s. Verranno usati i dati di fallback.",
                                response.status,
                                self.url,
                            )
            except Exception as err:
                _LOGGER.warning(
                    "Impossibile contattare l'endpoint ARERA %s (%s). Vengono utilizzati i valori predefiniti.",
                    self.url,
                    err,
                )

        return data
