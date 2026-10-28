"""Config Flow per ARERA Tariffe (Energia Elettrica o Gas Naturale)."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_GAS_AMBITO,
    CONF_GAS_SCAGLIONE,
    CONF_SCAN_INTERVAL,
    CONF_SERVICE_TYPE,
    CONF_SOURCE_TYPE,
    CONF_URL,
    DEFAULT_GAS_AMBITO,
    DEFAULT_GAS_SCAGLIONE,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DEFAULT_URL,
    DOMAIN,
    GAS_AMBITI,
    GAS_SCAGLIONI,
    SERVICE_TYPE_ELECTRICITY,
    SERVICE_TYPE_GAS,
    SERVICES_OPTIONS,
    SOURCE_TYPE_ARERA_XLSX,
    SOURCE_TYPE_CUSTOM_URL,
    SOURCE_TYPE_MANUAL,
    get_arera_stg_urls,
)


class AreraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestione del Config Flow per ARERA."""

    VERSION = 1

    def __init__(self) -> None:
        """Inizializza il flow."""
        self._service_type: str = SERVICE_TYPE_ELECTRICITY

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Primo step: scelta del servizio (Energia Elettrica o Gas Naturale)."""
        if user_input is not None:
            self._service_type = user_input[CONF_SERVICE_TYPE]
            if self._service_type == SERVICE_TYPE_GAS:
                return await self.async_step_gas()
            return await self.async_step_electricity()

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SERVICE_TYPE, default=SERVICE_TYPE_ELECTRICITY
                ): vol.In(SERVICES_OPTIONS),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    async def async_step_electricity(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configurazione per l'Energia Elettrica."""
        errors: dict[str, str] = {}

        if user_input is not None:
            unique_id = "arera_tariffe_electricity"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            user_input[CONF_SERVICE_TYPE] = SERVICE_TYPE_ELECTRICITY
            if user_input.get(CONF_SOURCE_TYPE) == SOURCE_TYPE_ARERA_XLSX:
                user_input[CONF_URL] = get_arera_stg_urls()[0]

            return self.async_create_entry(
                title="ARERA Tariffe Energia Elettrica",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SOURCE_TYPE, default=SOURCE_TYPE_ARERA_XLSX
                ): vol.In(
                    {
                        SOURCE_TYPE_ARERA_XLSX: "Tabelle Ufficiali ARERA Online (.xlsx)",
                        SOURCE_TYPE_CUSTOM_URL: "URL Personalizzato (JSON o Excel)",
                        SOURCE_TYPE_MANUAL: "Valori Ufficiali Predefiniti / Manuale",
                    }
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL_HOURS
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
            }
        )

        return self.async_show_form(
            step_id="electricity",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_gas(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configurazione per il Gas Naturale."""
        errors: dict[str, str] = {}

        if user_input is not None:
            unique_id = "arera_tariffe_gas"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            user_input[CONF_SERVICE_TYPE] = SERVICE_TYPE_GAS
            if user_input.get(CONF_SOURCE_TYPE) == SOURCE_TYPE_ARERA_XLSX:
                user_input[CONF_URL] = "https://www.arera.it/fileadmin/area_operatori/prezzi_e_tariffe/G2026_stv.xlsx"

            return self.async_create_entry(
                title="ARERA Tariffe Gas Naturale",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_GAS_AMBITO, default=DEFAULT_GAS_AMBITO
                ): vol.In(GAS_AMBITI),
                vol.Required(
                    CONF_GAS_SCAGLIONE, default=DEFAULT_GAS_SCAGLIONE
                ): vol.In(GAS_SCAGLIONI),
                vol.Required(
                    CONF_SOURCE_TYPE, default=SOURCE_TYPE_ARERA_XLSX
                ): vol.In(
                    {
                        SOURCE_TYPE_ARERA_XLSX: "Tabelle Ufficiali ARERA Online (.xlsx)",
                        SOURCE_TYPE_CUSTOM_URL: "URL Personalizzato (JSON o Excel)",
                        SOURCE_TYPE_MANUAL: "Valori Ufficiali Predefiniti / Manuale",
                    }
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL_HOURS
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
            }
        )

        return self.async_show_form(
            step_id="gas",
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
        """Gestisce le opzioni modificabili in base al servizio dell'entry."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        entry = self.config_entry
        service_type = entry.data.get(CONF_SERVICE_TYPE, SERVICE_TYPE_ELECTRICITY)
        current_scan = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS),
        )

        schema_dict: dict[Any, Any] = {}

        if service_type == SERVICE_TYPE_GAS:
            current_ambito = entry.options.get(
                CONF_GAS_AMBITO, entry.data.get(CONF_GAS_AMBITO, DEFAULT_GAS_AMBITO)
            )
            current_scaglione = entry.options.get(
                CONF_GAS_SCAGLIONE, entry.data.get(CONF_GAS_SCAGLIONE, DEFAULT_GAS_SCAGLIONE)
            )
            schema_dict[vol.Required(CONF_GAS_AMBITO, default=current_ambito)] = vol.In(GAS_AMBITI)
            schema_dict[vol.Required(CONF_GAS_SCAGLIONE, default=current_scaglione)] = vol.In(GAS_SCAGLIONI)

        schema_dict[
            vol.Optional(
                CONF_SCAN_INTERVAL, default=int(current_scan)
            )
        ] = vol.All(vol.Coerce(int), vol.Range(min=1, max=168))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
        )
