from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, REG_MAX_CURRENT
from .coordinator import AnkerSolixCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coord: AnkerSolixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MaxCurrentNumber(coord, entry)])

class MaxCurrentNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Max Current"
    _attr_native_unit_of_measurement = "A"
    _attr_native_min_value = 0
    _attr_native_max_value = 32
    _attr_native_step = 1

    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        self.entry = entry

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_max_current"

    @property
    def native_value(self):
        # MVP: on ne relit pas en continu 21004 (on pourrait l’ajouter au coordinator si tu veux)
        return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.write_u16(REG_MAX_CURRENT, int(value))
        await self.coordinator.async_request_refresh()

