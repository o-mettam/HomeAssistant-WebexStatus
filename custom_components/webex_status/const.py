"""Constants for the Webex Status integration."""

DOMAIN = "webex_status"

CONF_BOT_TOKEN = "bot_token"
CONF_PERSON_ID = "person_id"

DEFAULT_SCAN_INTERVAL = 15  # seconds

WEBEX_API_BASE = "https://webexapis.com/v1"

WEBEX_STATUS_MAP = {
    "active": "Active",
    "call": "In a Call",
    "DoNotDisturb": "Do Not Disturb",
    "inactive": "Inactive",
    "meeting": "In a Meeting",
    "presenting": "Presenting",
    "OutOfOffice": "Out of Office",
    "pending": "Pending",
}
