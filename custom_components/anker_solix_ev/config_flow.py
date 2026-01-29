from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_ADDRESS_OFFSET, CONF_WORD_ORDER,
    DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_ADDRESS_OFFSET, DEFAULT_WORD_ORDER,
)


class AnkerSolixEVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            # Uniqueness by host:port
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Anker SOLIX EV ({user_input[CONF_HOST]})",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int),
            vol.Optional(CONF_ADDRESS_OFFSET, default=DEFAULT_ADDRESS_OFFSET): vol.In([0, -1]),
            vol.Optional(CONF_WORD_ORDER, default=DEFAULT_WORD_ORDER): vol.In(["hi_lo", "lo_hi"]),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AnkerSolixEVOptionsFlow(config_entry)


class AnkerSolixEVOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        schema = vol.Schema({
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=data.get(CONF_PORT, DEFAULT_PORT)): vol.Coerce(int),
            vol.Required(CONF_SCAN_INTERVAL, default=data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.Coerce(int),
            vol.Required(CONF_ADDRESS_OFFSET, default=data.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET)): vol.In([0, -1]),
            vol.Required(CONF_WORD_ORDER, default=data.get(CONF_WORD_ORDER, DEFAULT_WORD_ORDER)): vol.In(["hi_lo", "lo_hi"]),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
