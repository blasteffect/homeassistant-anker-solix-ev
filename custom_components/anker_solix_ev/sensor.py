from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CHARGING_STATUS_MAP,
)
from .coordinator import AnkerSolixCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coord: AnkerSolixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ChargingStatusSensor(coord, entry),
        TotalActivePowerSensor(coord, entry),
        U32Sensor(coord, entry, "Session Energy", "energy_wh", "Wh"),
    ])


class _Base(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        self.entry = entry

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class ChargingStatusSensor(_Base):
    _attr_name = "Charging Status"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_charging_status"

    @property
    def native_value(self):
        raw = self.coordinator.data.get("charging_status")
        if raw is None:
            return None
        raw = int(raw)
        return CHARGING_STATUS_MAP.get(raw, f"unknown_{raw}")


class U16Sensor(_Base):
    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str, unit: str | None):
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._attr_native_unit_of_measurement = unit

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._key)
        return int(val) if val is not None else None


class U32Sensor(_Base):
    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str, unit: str | None):
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._attr_native_unit_of_measurement = unit

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._key)
        return int(val) if val is not None else None


class ScaledU16Sensor(_Base):
    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str, unit: str, gain: int):
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._attr_native_unit_of_measurement = unit
        self._gain = gain

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None
        return float(int(raw)) / float(self._gain)


class EnumSensor(_Base):
    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str, mapping: dict[int, str]):
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._map = mapping

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None
        raw = int(raw)
        return self._map.get(raw, f"unknown_{raw}")

class TotalActivePowerSensor(_Base):
    _attr_name = "Total Active Power"
    _attr_native_unit_of_measurement = "W"
    _attr_device_class = "power"
    _attr_state_class = "measurement"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_power_w"

    @property
    def native_value(self):
        val = self.coordinator.data.get("power_w")
        return int(val) if val is not None else None
