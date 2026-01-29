from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AnkerSolixCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    coord: AnkerSolixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            _FlagBinarySensor(coord, entry, "PWM Enabled", "pwm_enabled"),
            _FlagBinarySensor(coord, entry, "Load Balancing Enabled", "load_balancing_enabled"),
            _FlagBinarySensor(coord, entry, "Solar Balancing Enabled", "solar_balancing_enabled"),
            _FlagBinarySensor(coord, entry, "CP Signal Status", "cp_signal_status"),
        ]
    )


class _FlagBinarySensor(BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str):
        self.coordinator = coordinator
        self.entry = entry
        self._attr_name = name
        self._key = key

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def is_on(self):
        val = self.coordinator.data.get(self._key)
        if val is None:
            return None
        return int(val) == 1

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
