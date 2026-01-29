from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_ADDRESS_OFFSET, CONF_WORD_ORDER,
    REG_CHARGING_STATUS, REG_TOTAL_ACTIVE_POWER, REG_SESSION_DURATION, REG_SESSION_ENERGY_WH,
)
from .modbus_client import AnkerModbusClient, ModbusSettings

class AnkerSolixCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        data = entry.data

        settings = ModbusSettings(
            host=data[CONF_HOST],
            port=data[CONF_PORT],
            address_offset=data.get(CONF_ADDRESS_OFFSET, 0),
            word_order=data.get(CONF_WORD_ORDER, "hi_lo"),
        )
        self.client = AnkerModbusClient(settings)

        scan = int(data.get(CONF_SCAN_INTERVAL, 5))
        super().__init__(
            hass,
            logger=None,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=scan),
        )

    async def _async_update_data(self) -> dict:
        try:
            status = await self.client.read_u16(REG_CHARGING_STATUS)
            power_w = await self.client.read_u32(REG_TOTAL_ACTIVE_POWER)
            duration_s = await self.client.read_u32(REG_SESSION_DURATION)
            energy_wh = await self.client.read_u32(REG_SESSION_ENERGY_WH)

            return {
                "charging_status": status,
                "power_w": power_w,
                "duration_s": duration_s,
                "energy_wh": energy_wh,
            }
        except Exception as err:
            raise UpdateFailed(str(err)) from err

