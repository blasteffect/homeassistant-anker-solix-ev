from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_ADDRESS_OFFSET, CONF_WORD_ORDER,
    DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_ADDRESS_OFFSET, DEFAULT_WORD_ORDER,
    REG_CHARGING_STATUS, REG_TOTAL_ACTIVE_POWER, REG_SESSION_DURATION, REG_SESSION_ENERGY_WH,
    REG_PHASE_SETTING, REG_MAX_CURRENT,
    REG_L1N_VOLTAGE, REG_L2N_VOLTAGE, REG_L3N_VOLTAGE, REG_L12_VOLTAGE, REG_L23_VOLTAGE, REG_L31_VOLTAGE,
    REG_L1_CURRENT, REG_L2_CURRENT, REG_L3_CURRENT,
    REG_L1_ACTIVE_POWER, REG_L2_ACTIVE_POWER, REG_L3_ACTIVE_POWER,
    REG_L1_REACTIVE_POWER, REG_L2_REACTIVE_POWER, REG_L3_REACTIVE_POWER,
    REG_L1_APPARENT_POWER, REG_L2_APPARENT_POWER, REG_L3_APPARENT_POWER,
    REG_OPERATING_MODE, REG_PWM_ENABLED, REG_CHARGING_MODE,
    REG_CP_SIGNAL_STATUS, REG_LOAD_BALANCING_ENABLED, REG_SOLAR_BALANCING_ENABLED,
    REG_CP_ACQ_VOLTAGE, REG_LED_BRIGHTNESS,
    REG_RELAY1_TEMP, REG_RELAY2_TEMP,
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
        self._word_order = word_order

        self.client = AnkerModbusClient(
            ModbusSettings(
                host=host,
                port=port,
                address_offset=offset,
                word_order=word_order,
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
            block_20053_20085 = await self.client.read_block(20053, 33)
            block_20086 = await self.client.read_block(20086, 1)
            block_20089_20090 = await self.client.read_block(20089, 2)
            block_20092_20099 = await self.client.read_block(20092, 8)

            def u16(register: int) -> int:
                if 20053 <= register <= 20085:
                    return int(block_20053_20085[register - 20053])
                if register == 20086:
                    return int(block_20086[0])
                if 20089 <= register <= 20090:
                    return int(block_20089_20090[register - 20089])
                if 20092 <= register <= 20099:
                    return int(block_20092_20099[register - 20092])
                raise ValueError(f"Register {register} is outside cached read blocks")

            def u32(register: int) -> int:
                w0, w1 = u16(register), u16(register + 1)
                if self._word_order == "hi_lo":
                    hi, lo = w0, w1
                else:
                    hi, lo = w1, w0
                return (hi << 16) | lo

            status = u16(REG_CHARGING_STATUS)
            power_w = u32(REG_TOTAL_ACTIVE_POWER)
            duration_s = u32(REG_SESSION_DURATION)
            energy_wh = u32(REG_SESSION_ENERGY_WH)

            phase = await self.client.read_u16(REG_PHASE_SETTING)
            max_current = await self.client.read_u16(REG_MAX_CURRENT)

            v_l1n = u16(REG_L1N_VOLTAGE)
            v_l2n = u16(REG_L2N_VOLTAGE)
            v_l3n = u16(REG_L3N_VOLTAGE)
            v_l12 = u16(REG_L12_VOLTAGE)
            v_l23 = u16(REG_L23_VOLTAGE)
            v_l31 = u16(REG_L31_VOLTAGE)

            i_l1 = u16(REG_L1_CURRENT)
            i_l2 = u16(REG_L2_CURRENT)
            i_l3 = u16(REG_L3_CURRENT)

            p_l1 = u32(REG_L1_ACTIVE_POWER)
            p_l2 = u32(REG_L2_ACTIVE_POWER)
            p_l3 = u32(REG_L3_ACTIVE_POWER)

            q_l1 = u32(REG_L1_REACTIVE_POWER)
            q_l2 = u32(REG_L2_REACTIVE_POWER)
            q_l3 = u32(REG_L3_REACTIVE_POWER)

            s_l1 = u32(REG_L1_APPARENT_POWER)
            s_l2 = u32(REG_L2_APPARENT_POWER)
            s_l3 = u32(REG_L3_APPARENT_POWER)

            operating_mode = u16(REG_OPERATING_MODE)
            pwm_enabled = u16(REG_PWM_ENABLED)
            charging_mode = u16(REG_CHARGING_MODE)

            cp_signal = u16(REG_CP_SIGNAL_STATUS)
            lb_enabled = u16(REG_LOAD_BALANCING_ENABLED)
            solar_enabled = u16(REG_SOLAR_BALANCING_ENABLED)
            cp_acq = u16(REG_CP_ACQ_VOLTAGE)
            led = u16(REG_LED_BRIGHTNESS)

            relay1 = u16(REG_RELAY1_TEMP)
            relay2 = u16(REG_RELAY2_TEMP)

            return {
                "charging_status": status,
                "power_w": power_w,
                "duration_s": duration_s,
                "energy_wh": energy_wh,
                "phase_setting": phase,
                "max_current": max_current,

                "v_l1n": v_l1n, "v_l2n": v_l2n, "v_l3n": v_l3n,
                "v_l12": v_l12, "v_l23": v_l23, "v_l31": v_l31,

                "i_l1": i_l1, "i_l2": i_l2, "i_l3": i_l3,

                "p_l1": p_l1, "p_l2": p_l2, "p_l3": p_l3,
                "q_l1": q_l1, "q_l2": q_l2, "q_l3": q_l3,
                "s_l1": s_l1, "s_l2": s_l2, "s_l3": s_l3,

                "operating_mode": operating_mode,
                "pwm_enabled": pwm_enabled,
                "charging_mode": charging_mode,
                "cp_signal_status": cp_signal,
                "load_balancing_enabled": lb_enabled,
                "solar_balancing_enabled": solar_enabled,
                "cp_acq_voltage": cp_acq,
                "led_brightness": led,

                "relay1_temp": relay1,
                "relay2_temp": relay2,
            }
        except Exception as err:
            raise UpdateFailed(str(err)) from err
