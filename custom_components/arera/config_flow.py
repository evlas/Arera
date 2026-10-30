"""Config Flow per ARERA Tariffe (Energia Elettrica o Gas Naturale)."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

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
    DOMAIN,
    GAS_AMBITI,
    GAS_SCAGLIONI,
    SERVICE_TYPE_ELECTRICITY,
    SERVICE_TYPE_GAS,
    SERVICES_OPTIONS,
    SOURCE_TYPE_ARERA_XLSX,
    SOURCE_TYPE_CUSTOM_URL,
    SOURCE_TYPE_MANUAL,
    get_arera_gas_urls,
    get_arera_stg_urls,
)

SOURCE_OPTIONS = [
    SOURCE_TYPE_ARERA_XLSX,
    SOURCE_TYPE_CUSTOM_URL,
    SOURCE_TYPE_MANUAL,
]


def _validate_custom_url(user_input: dict[str, Any], errors: dict[str, str]) -> str:
    """Valida il campo URL quando è selezionata la sorgente personalizzata."""
    raw_url = str(user_input.get(CONF_URL, "") or "").strip()
    if user_input.get(CONF_SOURCE_TYPE) == SOURCE_TYPE_CUSTOM_URL:
        if not raw_url or not (raw_url.startswith("http://") or raw_url.startswith("https://")):
            errors[CONF_URL] = "invalid_url"
    return raw_url


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
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(SERVICES_OPTIONS.keys()),
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="service_type",
                    )
                ),
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
            custom_url = _validate_custom_url(user_input, errors)
            if not errors:
                unique_id = "arera_tariffe_electricity"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                user_input[CONF_SERVICE_TYPE] = SERVICE_TYPE_ELECTRICITY
                if user_input.get(CONF_SOURCE_TYPE) == SOURCE_TYPE_ARERA_XLSX:
                    user_input[CONF_URL] = get_arera_stg_urls()[0]
                elif custom_url:
                    user_input[CONF_URL] = custom_url

                return self.async_create_entry(
                    title="ARERA Tariffe Energia Elettrica",
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SOURCE_TYPE, default=SOURCE_TYPE_ARERA_XLSX
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=SOURCE_OPTIONS,
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="source_type",
                    )
                ),
                vol.Optional(CONF_URL, default=""): cv.string,
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
            custom_url = _validate_custom_url(user_input, errors)
            if not errors:
                unique_id = "arera_tariffe_gas"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                user_input[CONF_SERVICE_TYPE] = SERVICE_TYPE_GAS
                if user_input.get(CONF_SOURCE_TYPE) == SOURCE_TYPE_ARERA_XLSX:
                    user_input[CONF_URL] = get_arera_gas_urls()[0]
                elif custom_url:
                    user_input[CONF_URL] = custom_url

                return self.async_create_entry(
                    title="ARERA Tariffe Gas Naturale",
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_GAS_AMBITO, default=DEFAULT_GAS_AMBITO
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(GAS_AMBITI.keys()),
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="gas_ambito",
                    )
                ),
                vol.Required(
                    CONF_GAS_SCAGLIONE, default=DEFAULT_GAS_SCAGLIONE
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(GAS_SCAGLIONI.keys()),
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="gas_scaglione",
                    )
                ),
                vol.Required(
                    CONF_SOURCE_TYPE, default=SOURCE_TYPE_ARERA_XLSX
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=SOURCE_OPTIONS,
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="source_type",
                    )
                ),
                vol.Optional(CONF_URL, default=""): cv.string,
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
        errors: dict[str, str] = {}
        entry = self.config_entry
        service_type = entry.data.get(CONF_SERVICE_TYPE, SERVICE_TYPE_ELECTRICITY)

        if user_input is not None:
            custom_url = _validate_custom_url(user_input, errors)
            if not errors:
                if user_input.get(CONF_SOURCE_TYPE) == SOURCE_TYPE_ARERA_XLSX:
                    user_input[CONF_URL] = (
                        get_arera_gas_urls()[0]
                        if service_type == SERVICE_TYPE_GAS
                        else get_arera_stg_urls()[0]
                    )
                elif custom_url:
                    user_input[CONF_URL] = custom_url
                return self.async_create_entry(title="", data=user_input)

        current_scan = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS),
        )
        current_source = entry.options.get(
            CONF_SOURCE_TYPE,
            entry.data.get(CONF_SOURCE_TYPE, SOURCE_TYPE_ARERA_XLSX),
        )
        current_url = entry.options.get(
            CONF_URL,
            entry.data.get(CONF_URL, ""),
        )

        schema_dict: dict[Any, Any] = {}

        if service_type == SERVICE_TYPE_GAS:
            current_ambito = entry.options.get(
                CONF_GAS_AMBITO, entry.data.get(CONF_GAS_AMBITO, DEFAULT_GAS_AMBITO)
            )
            current_scaglione = entry.options.get(
                CONF_GAS_SCAGLIONE, entry.data.get(CONF_GAS_SCAGLIONE, DEFAULT_GAS_SCAGLIONE)
            )
            schema_dict[vol.Required(CONF_GAS_AMBITO, default=current_ambito)] = SelectSelector(
                SelectSelectorConfig(
                    options=list(GAS_AMBITI.keys()),
                    mode=SelectSelectorMode.DROPDOWN,
                    translation_key="gas_ambito",
                )
            )
            schema_dict[vol.Required(CONF_GAS_SCAGLIONE, default=current_scaglione)] = SelectSelector(
                SelectSelectorConfig(
                    options=list(GAS_SCAGLIONI.keys()),
                    mode=SelectSelectorMode.DROPDOWN,
                    translation_key="gas_scaglione",
                )
            )

        schema_dict[vol.Required(CONF_SOURCE_TYPE, default=current_source)] = SelectSelector(
            SelectSelectorConfig(
                options=SOURCE_OPTIONS,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="source_type",
            )
        )
        schema_dict[vol.Optional(CONF_URL, default=str(current_url or ""))] = cv.string
        schema_dict[
            vol.Optional(
                CONF_SCAN_INTERVAL, default=int(current_scan)
            )
        ] = vol.All(vol.Coerce(int), vol.Range(min=1, max=168))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
        )
