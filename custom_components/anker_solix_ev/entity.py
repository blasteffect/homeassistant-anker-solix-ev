from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AnkerSolixCoordinator


class AnkerSolixEntity(CoordinatorEntity[AnkerSolixCoordinator]):
    """Base entity belonging to a single Anker SOLIX EV charger."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Anker",
            model="SOLIX V1 Smart EV Charger",
            name="Anker EV Charger",
        )
