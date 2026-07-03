"""Config flow for Baby Tracker integration."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_TOKEN, CONF_API_URL, CONF_BABY_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_URL, default="http://tu-servidor:3000/api/ha/overview"): str,
        vol.Required(CONF_BABY_ID): str,
        vol.Optional(CONF_API_TOKEN, default=""): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    headers = {}
    if data.get(CONF_API_TOKEN):
        headers["Authorization"] = f"Bearer {data[CONF_API_TOKEN]}"

    url = f"{data[CONF_API_URL].rstrip('/')}?baby_id={data[CONF_BABY_ID]}"
    
    async with session.get(url, headers=headers, timeout=10) as response:
        if response.status != 200:
            raise ConnectionError("cannot_connect")
        result = await response.json()

    return {"title": result.get("name", "Baby Tracker")}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Baby Tracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )