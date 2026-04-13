"""Sensor platform for the Webex Status integration."""

from __future__ import annotations

from datetime import timedelta
import logging
import time

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_BOT_TOKEN,
    CONF_PERSON_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    WEBEX_API_BASE,
    WEBEX_STATUS_MAP,
)

_LOGGER = logging.getLogger(__name__)

STATUS_ICONS = {
    "active": "mdi:account-check",
    "call": "mdi:phone-in-talk",
    "DoNotDisturb": "mdi:minus-circle",
    "inactive": "mdi:account-off",
    "meeting": "mdi:monitor-cellphone",
    "presenting": "mdi:presentation",
    "OutOfOffice": "mdi:briefcase-off",
    "pending": "mdi:account-clock",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Webex Status sensor from a config entry."""
    bot_token = entry.data[CONF_BOT_TOKEN]
    person_id = entry.data[CONF_PERSON_ID]

    coordinator = WebexStatusCoordinator(hass, bot_token, person_id)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([WebexStatusSensor(coordinator, entry)])


class WebexStatusCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch Webex status at a regular interval."""

    def __init__(
        self, hass: HomeAssistant, bot_token: str, person_id: str
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Webex Status",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._bot_token = bot_token
        self._person_id = person_id
        self._rate_limited_until: float = 0

    async def _async_update_data(self) -> dict:
        """Fetch data from the Webex People API."""
        # Respect rate limit back-off window
        now = time.monotonic()
        if now < self._rate_limited_until:
            wait = int(self._rate_limited_until - now)
            _LOGGER.debug("Rate limit back-off active, skipping for %ss", wait)
            if self.data is not None:
                return self.data
            raise UpdateFailed(
                f"Rate limited by Webex API, retrying in {wait}s"
            )

        session = async_get_clientsession(self.hass)
        headers = {"Authorization": f"Bearer {self._bot_token}"}
        url = f"{WEBEX_API_BASE}/people/{self._person_id}"

        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 429:
                    retry_after = int(
                        response.headers.get("Retry-After", DEFAULT_SCAN_INTERVAL)
                    )
                    self._rate_limited_until = time.monotonic() + retry_after
                    _LOGGER.warning(
                        "Webex API rate limit hit, backing off for %ss",
                        retry_after,
                    )
                    if self.data is not None:
                        return self.data
                    raise UpdateFailed(
                        f"Rate limited by Webex API, retrying in {retry_after}s"
                    )
                if response.status != 200:
                    raise UpdateFailed(
                        f"Webex API returned HTTP {response.status}"
                    )
                return await response.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Webex API: {err}") from err


class WebexStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity representing a Webex user's status."""

    _attr_has_entity_name = True
    _attr_translation_key = "webex_status"

    def __init__(
        self,
        coordinator: WebexStatusCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_PERSON_ID]}_status"
        self._entry = entry

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        display_name = self.coordinator.data.get("displayName", "Webex User")
        return f"{display_name} Webex Status"

    @property
    def native_value(self) -> str | None:
        """Return the current Webex status."""
        return self.coordinator.data.get("status")

    @property
    def icon(self) -> str:
        """Return an icon based on the current status."""
        status = self.coordinator.data.get("status", "")
        return STATUS_ICONS.get(status, "mdi:account-question")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes from the Webex API response."""
        data = self.coordinator.data
        friendly = WEBEX_STATUS_MAP.get(data.get("status", ""), "Unknown")
        return {
            "status": data.get("status"),
            "friendly_status": friendly,
            "display_name": data.get("displayName"),
            "emails": data.get("emails", []),
            "avatar": data.get("avatar"),
            "last_activity": data.get("lastActivity"),
        }

    @property
    def entity_picture(self) -> str | None:
        """Return the Webex user's avatar as the entity picture."""
        return self.coordinator.data.get("avatar")
