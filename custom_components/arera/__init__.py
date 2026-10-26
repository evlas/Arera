"""Integrazione ARERA Tariffe Luce per Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN
from .coordinator import AreraDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Imposta ARERA da ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})

    integration_version: str | None = None
    try:
        integration = await async_get_integration(hass, DOMAIN)
        if integration.version is not None:
            integration_version = str(integration.version)
    except Exception:
        pass

    coordinator = AreraDataUpdateCoordinator(hass, entry, version=integration_version)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Rimuove una voce di configurazione ARERA."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Gestisce l'aggiornamento delle opzioni."""
    await hass.config_entries.async_reload(entry.entry_id)
