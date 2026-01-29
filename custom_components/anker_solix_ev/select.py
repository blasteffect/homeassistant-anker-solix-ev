from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, REG_PHASE_SETTING, PHASE_MAP, PHASE_REVERSE_MAP
from .coordinator import AnkerSolixCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coord: AnkerSolixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PhaseSelect(coord, entry)])

class PhaseSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Phase Setting"
    _attr_options = list(PHASE_REVERSE_MAP.keys())

    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        self.entry = entry

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_phase_setting"

    @property
    def current_option(self):
        return None  # MVP (on peut lire 21003 et l’exposer si tu veux)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.write_u16(REG_PHASE_SETTING, PHASE_REVERSE_MAP[option])
        await self.coordinator.async_request_refresh()

