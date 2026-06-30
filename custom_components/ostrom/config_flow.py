from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_ZIP, CONF_ENV, CONF_ENDPOINT, DEFAULT_ENV, DEFAULT_ENDPOINT

class OstromConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title='Ostrom Energy by 9rn.de', data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_CLIENT_ID): str,
            vol.Required(CONF_CLIENT_SECRET): str,
            vol.Required(CONF_ZIP): str,
            vol.Required(CONF_ENV, default=DEFAULT_ENV): selector.SelectSelector(selector.SelectSelectorConfig(options=['production', 'development'], mode=selector.SelectSelectorMode.DROPDOWN)),
            vol.Required(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): str,
        })
        return self.async_show_form(step_id='user', data_schema=schema)
