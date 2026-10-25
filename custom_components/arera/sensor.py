"""Piattaforma sensori per ARERA Tariffe."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES
from .coordinator import AreraDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura i sensori ARERA da ConfigEntry."""
    coordinator: AreraDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        AreraSensor(coordinator, entry, key, meta)
        for key, meta in SENSOR_TYPES.items()
    ]

    async_add_entities(entities)


class AreraSensor(CoordinatorEntity[AreraDataUpdateCoordinator], SensorEntity):
    """Rappresentazione di un sensore tariffario ARERA."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AreraDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
        meta: dict[str, Any],
    ) -> None:
        """Inizializza il sensore."""
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = meta.get("unit")
        self._attr_icon = meta.get("icon", "mdi:cash")
        if meta.get("unit") is not None:
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_suggested_display_precision = 6 if "kWh" in (meta.get("unit") or "") else 4

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="ARERA Tariffe Regolate",
            manufacturer="ARERA",
            model="Tariffe Bassa Tensione Domestici",
        )

    @property
    def native_value(self) -> Any:
        """Restituisce il valore del sensore."""
        return self.coordinator.data.get(self._key)
