"""Config flow for Koszty Energii."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import CONF_SOURCE_ENTITY, DEFAULT_NAME, DOMAIN


class KosztyEnergiiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Koszty Energii."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_SOURCE_ENTITY])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_import(self, user_input):
        """Handle import from YAML."""
        if CONF_NAME not in user_input:
            user_input[CONF_NAME] = DEFAULT_NAME
        await self.async_set_unique_id(user_input[CONF_SOURCE_ENTITY])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
