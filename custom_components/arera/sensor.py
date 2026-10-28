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
            sw_version=str(coordinator.version) if coordinator.version else "1.1.0",
        )

    @property
    def available(self) -> bool:
        """Il sensore è disponibile solo se il coordinator è attivo e il valore è presente."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.get(self._key) is not None
        )

    @property
    def native_value(self) -> Any:
        """Restituisce il valore del sensore."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Restituisce attributi di stato addizionali come il periodo/mese dei dati."""
        attrs: dict[str, Any] = {}
        if not self.coordinator.data:
            return attrs

        period = self.coordinator.data.get("period") or self.coordinator.data.get("today")
        if period:
            attrs["periodo"] = period
            attrs["period"] = period
        if "sheet_name" in self.coordinator.data:
            attrs["foglio_excel"] = self.coordinator.data["sheet_name"]
            attrs["sheet_name"] = self.coordinator.data["sheet_name"]
        if "source_url" in self.coordinator.data:
            attrs["source_url"] = self.coordinator.data["source_url"]
        if "smt_sheet" in self.coordinator.data and self._key == "dispbt":
            attrs["foglio_smt"] = self.coordinator.data["smt_sheet"]
        if "last_update" in self.coordinator.data:
            attrs["ultimo_aggiornamento"] = self.coordinator.data["last_update"]

        return attrs
