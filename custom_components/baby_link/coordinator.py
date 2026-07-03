"""DataUpdateCoordinator for Baby Link."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_API_URL, CONF_BABY_ID, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class BabyLinkCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Baby Link data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.entry = entry
        self.api_url = entry.data[CONF_API_URL]
        self.baby_id = entry.data[CONF_BABY_ID]

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        session = async_get_clientsession(self.hass)

        base_url = self.api_url.rstrip("/")
        url = f"{base_url}/homeassistant/{self.baby_id}/summary" 

        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Error communicating with API: status {resp.status}")
                
                json_response = await resp.json()
                
                if isinstance(json_response, dict) and "data" in json_response:
                    return json_response["data"]
                    
                return json_response
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err