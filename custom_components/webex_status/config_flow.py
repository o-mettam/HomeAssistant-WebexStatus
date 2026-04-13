"""Config flow for the Webex Status integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_BOT_TOKEN, CONF_PERSON_ID, DOMAIN, WEBEX_API_BASE

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BOT_TOKEN): str,
        vol.Required(CONF_PERSON_ID): str,
    }
)


class WebexStatusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Webex Status."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate credentials by making a test API call
            try:
                session = async_get_clientsession(self.hass)
                headers = {
                    "Authorization": f"Bearer {user_input[CONF_BOT_TOKEN]}"
                }
                url = f"{WEBEX_API_BASE}/people/{user_input[CONF_PERSON_ID]}"

                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        display_name = data.get("displayName", "Webex User")

                        # Prevent duplicate entries for the same person
                        await self.async_set_unique_id(user_input[CONF_PERSON_ID])
                        self._abort_if_unique_id_configured()

                        return self.async_create_entry(
                            title=f"Webex Status - {display_name}",
                            data=user_input,
                        )
                    elif response.status == 401:
                        errors["base"] = "invalid_auth"
                    elif response.status == 404:
                        errors[CONF_PERSON_ID] = "person_not_found"
                    elif response.status == 429:
                        errors["base"] = "rate_limited"
                    else:
                        errors["base"] = "cannot_connect"

            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during Webex API validation")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "setup_guide_url": "https://github.com/owenmettam/HomeAssistant-WebexStatus"
            },
        )
