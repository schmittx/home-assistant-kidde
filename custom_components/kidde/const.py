"""Constants used by the Kidde integration."""

CONF_COOKIES = "cookies"
CONF_DEVICES = "devices"
CONF_SAVE_RESPONSES = "save_responses"
CONF_LOCATIONS = "locations"
CONF_TIMEOUT = "timeout"

DATA_COORDINATOR = "coordinator"

DOMAIN = "kidde"

UNDO_UPDATE_LISTENER = "undo_update_listener"

MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 600
STEP_SCAN_INTERVAL = 30

MIN_TIMEOUT = 10
MAX_TIMEOUT = 60
STEP_TIMEOUT = 5

DEFAULT_SAVE_LOCATION = f"/config/custom_components/{DOMAIN}/api/responses"
DEFAULT_SAVE_RESPONSES = False
DEFAULT_SCAN_INTERVAL = 120
DEFAULT_TIMEOUT = 30

DEVICE_MANUFACTURER = "Kidde"
