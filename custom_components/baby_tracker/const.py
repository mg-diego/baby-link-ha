"""Constants for the Baby Tracker integration."""
from datetime import timedelta

DOMAIN = "baby_tracker"
CONF_API_URL = "api_url"
CONF_BABY_ID = "baby_id"

DEFAULT_NAME = "Baby Tracker"
SCAN_INTERVAL = timedelta(seconds=60)