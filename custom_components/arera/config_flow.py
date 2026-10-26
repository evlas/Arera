"""Config Flow per ARERA Tariffe."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SOURCE_TYPE,
    CONF_URL,
    DEFAULT_ARERA_VALUES,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DEFAULT_URL,
    DOMAIN,
    OFFICIAL_ARERA_XLSX_URL,
    SOURCE_TYPE_ARERA_XLSX,
    SOURCE_TYPE_CUSTOM_URL,
    SOURCE_TYPE_MANUAL,
)


class AreraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestione del Config Flow per ARERA."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Primo step: scelta sorgente e configurazione iniziale."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id("arera_tariffe_luce")
            self._abort_if_unique_id_configured()

            # Se ha scelto l'Excel ufficiale, imposta l'URL ufficiale ARERA
            if user_input.get(CONF_SOURCE_TYPE) == SOURCE_TYPE_ARERA_XLSX:
                user_input[CONF_URL] = OFFICIAL_ARERA_XLSX_URL

            return self.async_create_entry(
                title="ARERA Tariffe Luce",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SOURCE_TYPE, default=SOURCE_TYPE_ARERA_XLSX
                ): vol.In(
                    {
                        SOURCE_TYPE_ARERA_XLSX: "Tabella Ufficiale ARERA Online (.xlsx)",
                        SOURCE_TYPE_CUSTOM_URL: "URL Personalizzato (JSON o Excel locale/remoto)",
                        SOURCE_TYPE_MANUAL: "Valori Ufficiali Predefiniti / Manuale",
                    }
                ),
                vol.Optional(
                    CONF_URL, default=DEFAULT_URL
                ): cv.string,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL_HOURS
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Restituisce il gestore delle opzioni."""
        return AreraOptionsFlowHandler(config_entry)


class AreraOptionsFlowHandler(config_entries.OptionsFlow):
    """Gestione dell'Options Flow per ARERA."""

    def __init__(self, config_entry: config_entries.ConfigEntry | None = None) -> None:
        """Inizializza evitando l'assegnazione diretta a self.config_entry (read-only su HA recente)."""
        self._config_entry_compat = config_entry

    @property
    def config_entry(self) -> config_entries.ConfigEntry:
        """Restituisce il config entry in modo compatibile sia con vecchie che con nuove versioni di HA."""
        try:
            entry = super().config_entry
            if entry is not None:
                return entry
        except Exception:
            pass
        return self._config_entry_compat

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gestisce le opzioni modificabili."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        entry = self.config_entry
        current_url = entry.options.get(
            CONF_URL, entry.data.get(CONF_URL, DEFAULT_URL)
        )
        current_scan = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS),
        )

        schema_dict: dict[Any, Any] = {
            vol.Optional(CONF_URL, default=current_url): cv.string,
            vol.Optional(
                CONF_SCAN_INTERVAL, default=int(current_scan)
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
        )
