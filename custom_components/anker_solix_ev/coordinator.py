from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_ADDRESS_OFFSET, CONF_WORD_ORDER,
    DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_ADDRESS_OFFSET, DEFAULT_WORD_ORDER,
    REG_CHARGING_STATUS, REG_TOTAL_ACTIVE_POWER, REG_SESSION_ENERGY_WH,
)
from .modbus_client import AnkerModbusClient, ModbusSettings

_LOGGER = logging.getLogger(__name__)


class AnkerSolixCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry

        # data = identité (host/port), options = paramètres modifiables
        data = entry.data
        opts = entry.options

        host = data[CONF_HOST]
        port = int(data.get(CONF_PORT, DEFAULT_PORT))

        scan = int(opts.get(CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)))
        offset = int(opts.get(CONF_ADDRESS_OFFSET, data.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET)))
        word_order = str(opts.get(CONF_WORD_ORDER, data.get(CONF_WORD_ORDER, DEFAULT_WORD_ORDER)))
        self.client = AnkerModbusClient(
            ModbusSettings(
                host=host,
                port=port,
                address_offset=offset,
                word_order=word_order,
                connect_timeout=2.0,
                response_timeout=2.0,
                retries=1,
                retry_delay_s=0.2,
            )
        )

        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=scan),
        )

    async def _async_update_data(self) -> dict:
        try:
            return await asyncio.wait_for(self._read_all_data(), timeout=30.0)
        except TimeoutError as err:
            raise UpdateFailed("Modbus refresh timeout after 30s") from err
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    async def _read_all_data(self) -> dict:
        status = await self.client.read_u16(REG_CHARGING_STATUS)
        power_w = await self.client.read_u32(REG_TOTAL_ACTIVE_POWER)
        energy_wh = await self.client.read_u32(REG_SESSION_ENERGY_WH)

        return {
            "charging_status": status,
            "power_w": power_w,
            "energy_wh": energy_wh,
        }
