"""Config flow for Baby Tracker integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_URL, CONF_BABY_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_API_URL, default="https://baby-link-production.up.railway.app"
        ): str,
        vol.Required(CONF_BABY_ID): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    session = async_get_clientsession(hass)
    base_url = data[CONF_API_URL].rstrip("/")
    url = f"{base_url}/events/last/{data[CONF_BABY_ID]}"

    try:
        async with session.get(url, timeout=10) as response:
            if response.status in (401, 403):
                raise InvalidAuth
            if response.status != 200:
                _LOGGER.error("API returned status code %s", response.status)
                raise CannotConnect

            result = await response.json()
    except (asyncio.TimeoutError, aiohttp.ClientError) as err:
        _LOGGER.error("Failed to connect to Baby Tracker API: %s", err)
        raise CannotConnect from err

    # Ensure the name falls back to a default if the API doesn't return one
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
            # Prevent adding the exact same Baby ID twice
            await self.async_set_unique_id(user_input[CONF_BABY_ID])
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""