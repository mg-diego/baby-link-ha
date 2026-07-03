"""DataUpdateCoordinator for Baby Tracker."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_API_TOKEN, CONF_API_URL, CONF_BABY_ID, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class BabyTrackerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Baby Tracker data."""

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
        self.token = entry.data.get(CONF_API_TOKEN)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        session = async_get_clientsession(self.hass)
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        url = f"{self.api_url.rstrip('/')}?baby_id={self.baby_id}"

        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Error communicating with API: status {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err