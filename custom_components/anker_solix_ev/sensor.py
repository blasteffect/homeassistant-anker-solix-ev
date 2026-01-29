from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CHARGING_STATUS_MAP
from .coordinator import AnkerSolixCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coord: AnkerSolixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ChargingStatusSensor(coord, entry),
        PowerSensor(coord, entry),
        SessionEnergySensor(coord, entry),
        SessionDurationSensor(coord, entry),
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
        raw = int(self.coordinator.data.get("charging_status", 0))
        return CHARGING_STATUS_MAP.get(raw, f"unknown_{raw}")

class PowerSensor(_Base):
    _attr_name = "Total Active Power"
    _attr_native_unit_of_measurement = "W"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_power_w"

    @property
    def native_value(self):
        return int(self.coordinator.data.get("power_w", 0))

class SessionEnergySensor(_Base):
    _attr_name = "Session Energy"
    _attr_native_unit_of_measurement = "Wh"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_energy_wh"

    @property
    def native_value(self):
        return int(self.coordinator.data.get("energy_wh", 0))

class SessionDurationSensor(_Base):
    _attr_name = "Session Duration"
    _attr_native_unit_of_measurement = "s"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_duration_s"

    @property
    def native_value(self):
        return int(self.coordinator.data.get("duration_s", 0))

