from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, REG_COMMAND
from .coordinator import AnkerSolixCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coord: AnkerSolixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        StartChargeButton(coord, entry),
        StopChargeButton(coord, entry),
    ])


class _Base(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        self.entry = entry


class StartChargeButton(_Base):
    _attr_name = "Start Charging"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_start"

    async def async_press(self) -> None:
        await self.coordinator.client.write_u16(REG_COMMAND, 1)
        await self.coordinator.async_request_refresh()


class StopChargeButton(_Base):
    _attr_name = "Stop Charging"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_stop"

    async def async_press(self) -> None:
        await self.coordinator.client.write_u16(REG_COMMAND, 2)
        await self.coordinator.async_request_refresh()
