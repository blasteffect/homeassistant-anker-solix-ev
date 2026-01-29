from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_ADDRESS_OFFSET,
    CONF_WORD_ORDER,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_ADDRESS_OFFSET,
    DEFAULT_WORD_ORDER,
)


class AnkerSolixEVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input.get(CONF_PORT, DEFAULT_PORT)}"
            )
            self._abort_if_unique_id_configured()

            # Identité équipement (host/port) dans data
            data = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
            }

            # Paramètres modifiables dans options
            options = {
                CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                CONF_ADDRESS_OFFSET: user_input.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET),
                CONF_WORD_ORDER: user_input.get(CONF_WORD_ORDER, DEFAULT_WORD_ORDER),
            }

            return self.async_create_entry(
                title=f"Anker SOLIX EV ({data[CONF_HOST]})",
                data=data,
                options=options,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int),
                vol.Optional(CONF_ADDRESS_OFFSET, default=DEFAULT_ADDRESS_OFFSET): vol.Coerce(int),
                vol.Optional(CONF_WORD_ORDER, default=DEFAULT_WORD_ORDER): vol.In(["hi_lo", "lo_hi"]),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return AnkerSolixEVOptionsFlow(config_entry)


class AnkerSolixEVOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        # IMPORTANT: sur certaines versions HA, OptionsFlow n’a pas __init__(config_entry)
        # et config_entry est une property read-only -> on doit remplir _config_entry.
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # HA va stocker ça dans entry.options automatiquement
            return self.async_create_entry(title="", data=user_input)

        opts = self.config_entry.options

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.Coerce(int),
                vol.Required(
                    CONF_ADDRESS_OFFSET,
                    default=opts.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET),
                ): vol.Coerce(int),
                vol.Required(
                    CONF_WORD_ORDER,
                    default=opts.get(CONF_WORD_ORDER, DEFAULT_WORD_ORDER),
                ): vol.In(["hi_lo", "lo_hi"]),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
