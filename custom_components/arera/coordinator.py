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
    SOURCE_TYPE_ARERA_XLSX,
    SOURCE_TYPE_CUSTOM_URL,
    SOURCE_TYPE_MANUAL,
    get_arera_smt_urls,
    get_arera_stg_urls,
)
from .parser import parse_arera_smt_xlsx, parse_arera_xlsx

_LOGGER = logging.getLogger(__name__)


class AreraDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator per gestire l'acquisizione dei dati ARERA dalla rete."""

    def __init__(self, hass: HomeAssistant, config_entry, version: str | None = None) -> None:
        """Inizializza il coordinator."""
        self.entry = config_entry
        self.version = str(version) if version is not None else None
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
        """Recupera i dati da ARERA via web o solleva UpdateFailed se mancanti/errati."""
        data: dict[str, Any] = {}

        # 1. Se modalità manuale, usa i valori configurati nelle opzioni o i predefiniti
        if self.source_type == SOURCE_TYPE_MANUAL:
            data = dict(DEFAULT_ARERA_VALUES)
            data["today"] = "Manuale / Predefinito"
            data["period"] = "Manuale / Predefinito"
            for key in DEFAULT_ARERA_VALUES:
                if key in self.entry.options:
                    try:
                        data[key] = float(self.entry.options[key])
                    except (ValueError, TypeError):
                        pass
            return data

        session = async_get_clientsession(self.hass)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 2. Acquisizione file principale (STG o Custom URL)
        stg_success = False
        last_stg_error: Exception | None = None

        if self.source_type == SOURCE_TYPE_ARERA_XLSX:
            urls_to_try = get_arera_stg_urls()
            # Se l'utente ha impostato un URL custom valido nelle opzioni, provalo prioritariamente
            configured_url = self.entry.options.get(CONF_URL, self.entry.data.get(CONF_URL))
            if configured_url and configured_url not in urls_to_try:
                urls_to_try.insert(0, configured_url)
        else:
            urls_to_try = [self.url]

        for target_url in urls_to_try:
            try:
                _LOGGER.debug("Tentativo download tariffe ARERA da %s", target_url)
                async with async_timeout.timeout(30):
                    async with session.get(target_url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.read()
                            if content.startswith(b"PK  ") or ".xlsx" in target_url.lower():
                                parsed = parse_arera_xlsx(content)
                                data.update(parsed)
                                data["source_url"] = target_url
                                stg_success = True
                                _LOGGER.info(
                                    "Tariffe ARERA scaricate e interpretate con successo da %s (%s)",
                                    target_url,
                                    parsed.get("period", ""),
                                )
                                break
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
                                            if k_lower in ("today", "data", "date", "aggiornamento", "period"):
                                                data["today"] = str(v)
                                                data["period"] = str(v)
                                        data["source_url"] = target_url
                                        stg_success = True
                                        break
                                except Exception as json_err:
                                    raise ValueError(
                                        f"Formato non supportato o JSON non valido: {json_err}"
                                    ) from json_err
                        else:
                            _LOGGER.debug("HTTP %s scaricando %s, passo al prossimo URL", response.status, target_url)
            except Exception as err:
                last_stg_error = err
                _LOGGER.debug("Errore download/parsing da %s: %s", target_url, err)

        if not stg_success:
            raise UpdateFailed(
                f"Impossibile acquisire le tariffe ARERA dalla rete. Ultimo errore: {last_stg_error}"
            )

        # 3. Acquisizione componente DispBT da file SMT se in modalità ufficiale
        if self.source_type == SOURCE_TYPE_ARERA_XLSX:
            smt_urls = get_arera_smt_urls()
            smt_success = False
            last_smt_error: Exception | None = None

            for smt_url in smt_urls:
                try:
                    async with async_timeout.timeout(20):
                        async with session.get(smt_url, headers=headers) as smt_resp:
                            if smt_resp.status == 200:
                                smt_content = await smt_resp.read()
                                if smt_content.startswith(b"PK  "):
                                    smt_data = parse_arera_smt_xlsx(smt_content)
                                    if "dispbt" in smt_data:
                                        data["dispbt"] = smt_data["dispbt"]
                                        data["dispbt_source_url"] = smt_url
                                        data["smt_sheet"] = smt_data.get("smt_sheet")
                                        smt_success = True
                                        _LOGGER.info(
                                            "DispBT ARERA (%s €/anno) acquisito con successo da %s",
                                            data["dispbt"],
                                            smt_url,
                                        )
                                        break
                except Exception as smt_err:
                    last_smt_error = smt_err
                    _LOGGER.debug("Errore recupero SMT da %s: %s", smt_url, smt_err)

            if not smt_success:
                if "dispbt" not in data:
                    raise UpdateFailed(
                        f"Impossibile acquisire il parametro DispBT da SMT ARERA: {last_smt_error}"
                    )

        # 4. Applicazione sovrascritture manuali (se impostate in Opzioni)
        for key in DEFAULT_ARERA_VALUES:
            if key in self.entry.options:
                try:
                    data[key] = float(self.entry.options[key])
                except (ValueError, TypeError):
                    pass

        data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        return data
