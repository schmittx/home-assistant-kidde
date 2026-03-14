"""Constants used by the Kidde integration."""

from enum import IntEnum

CONF_COOKIES = "cookies"
CONF_DEVICES = "devices"
CONF_SAVE_RESPONSES = "save_responses"
CONF_LOCATIONS = "locations"
CONF_TIMEOUT = "timeout"

DATA_COORDINATOR = "coordinator"

DOMAIN = "kidde"

UNDO_UPDATE_LISTENER = "undo_update_listener"

DEFAULT_SAVE_LOCATION = f"/config/custom_components/{DOMAIN}/api/responses"
DEFAULT_SAVE_RESPONSES = False

DEVICE_MANUFACTURER = "Kidde"


class ScanInterval(IntEnum):
    """Scan interval."""

    DEFAULT = 120
    MAX = 600
    MIN = 30
    STEP = 30


class Timeout(IntEnum):
    """Timeout."""

    DEFAULT = 30
    MAX = 60
    MIN = 10
    STEP = 5
