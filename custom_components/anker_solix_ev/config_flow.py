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
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
            self._abort_if_unique_id_configured()

            # On met l'IP/port dans data (identité de l'équipement)
            data = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
            }

            # Le reste en options (modifiable via la roue)
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
        super().__init__(config_entry)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # IMPORTANT: on laisse HA enregistrer ça dans entry.options
            return self.async_create_entry(title="", data=user_input)

        opts = self.config_entry.options
        data = self.config_entry.data

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

                # Affiché mais non modifiable ici (on garde l'identité en data)
                # Si tu veux rendre host/port modifiables, on peut aussi le faire,
                # mais c’est souvent mieux de supprimer/réajouter l'intégration pour ça.
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
