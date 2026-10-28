"""Piattaforma sensori per ARERA Tariffe (Luce e Gas)."""
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

from .const import (
    DOMAIN,
    GAS_SENSOR_TYPES,
    SENSOR_TYPES,
    SERVICE_TYPE_BOTH,
    SERVICE_TYPE_ELECTRICITY,
    SERVICE_TYPE_GAS,
)
from .coordinator import AreraDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura i sensori ARERA Luce e Gas da ConfigEntry."""
    coordinator: AreraDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # 1. Sensori Energia Elettrica (Luce)
    if coordinator.service_type in (SERVICE_TYPE_ELECTRICITY, SERVICE_TYPE_BOTH):
        for key, meta in SENSOR_TYPES.items():
            entities.append(AreraElectricitySensor(coordinator, entry, key, meta))

    # 2. Sensori Gas Naturale
    if coordinator.service_type in (SERVICE_TYPE_GAS, SERVICE_TYPE_BOTH):
        for key, meta in GAS_SENSOR_TYPES.items():
            entities.append(AreraGasSensor(coordinator, entry, key, meta))

    async_add_entities(entities)


class AreraBaseSensor(CoordinatorEntity[AreraDataUpdateCoordinator], SensorEntity):
    """Classe base per i sensori tariffari ARERA."""

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
            unit_str = meta.get("unit") or ""
            if "kWh" in unit_str or "Smc" in unit_str:
                self._attr_suggested_display_precision = 6
            else:
                self._attr_suggested_display_precision = 4

    @property
    def available(self) -> bool:
        """Il sensore è disponibile se il coordinator è attivo e il valore è presente."""
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


class AreraElectricitySensor(AreraBaseSensor):
    """Sensore tariffario per l'energia elettrica (Luce)."""

    def __init__(
        self,
        coordinator: AreraDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
        meta: dict[str, Any],
    ) -> None:
        super().__init__(coordinator, entry, key, meta)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_luce")},
            name="ARERA Tariffe Luce",
            manufacturer="ARERA",
            model="Tariffe Bassa Tensione Domestici",
            sw_version=str(coordinator.version) if coordinator.version else "1.1.0",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Restituisce attributi di stato addizionali."""
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


class AreraGasSensor(AreraBaseSensor):
    """Sensore tariffario per il gas naturale."""

    def __init__(
        self,
        coordinator: AreraDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
        meta: dict[str, Any],
    ) -> None:
        super().__init__(coordinator, entry, key, meta)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_gas")},
            name="ARERA Tariffe Gas",
            manufacturer="ARERA",
            model="Tariffe Gas Naturale Domestici",
            sw_version=str(coordinator.version) if coordinator.version else "1.1.0",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Restituisce attributi di stato addizionali per il gas."""
        attrs: dict[str, Any] = {}
        if not self.coordinator.data:
            return attrs

        period = self.coordinator.data.get("gas_periodo")
        if period:
            attrs["periodo"] = period
            attrs["period"] = period
        if "gas_ambito" in self.coordinator.data:
            attrs["ambito"] = self.coordinator.data["gas_ambito"]
        if "gas_scaglione" in self.coordinator.data:
            attrs["scaglione"] = self.coordinator.data["gas_scaglione"]
        if "gas_sheet_name" in self.coordinator.data:
            attrs["foglio_excel"] = self.coordinator.data["gas_sheet_name"]
        if "gas_source_url" in self.coordinator.data:
            attrs["source_url"] = self.coordinator.data["gas_source_url"]
        if "last_update" in self.coordinator.data:
            attrs["ultimo_aggiornamento"] = self.coordinator.data["last_update"]

        return attrs
