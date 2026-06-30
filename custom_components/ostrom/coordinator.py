from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OstromApi
from .const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_ENV, CONF_ENDPOINT, CONF_ZIP, DOMAIN

_LOGGER = logging.getLogger(__name__)

class OstromCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        self.api = OstromApi(
            entry.data[CONF_CLIENT_ID],
            entry.data[CONF_CLIENT_SECRET],
            entry.data[CONF_ZIP],
            entry.data.get(CONF_ENV, 'production'),
            entry.data.get(CONF_ENDPOINT, '/spot-prices'),
        )
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=1))

    async def _async_update_data(self):
        async with aiohttp.ClientSession() as session:
            result = await self.api.get_spot_prices(session)
            if not result.ok:
                raise UpdateFailed(result.error or f'HTTP {result.status_code}')
            return result.data
