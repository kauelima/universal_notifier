DOMAIN = "universal_notifier"

# --- Chiavi di Configurazione (config entry / YAML legacy) ---
CONF_CHANNELS = "channels"
CONF_ASSISTANT_NAME = "assistant_name"
CONF_DATE_FORMAT = "date_format"
CONF_GREETINGS = "greetings"
CONF_TIME_SLOTS = "time_slots"
CONF_DND = "dnd"
CONF_BOLD_PREFIX = "bold_prefix"
CONF_INCLUDE_TIME = "include_time"
CONF_PRIORITY_VOLUME = "priority_volume"
CONF_PERSON_ENTITIES = "person_entities"

# --- Chiavi Parametri Servizio (Service Call) ---
CONF_MESSAGE = "message"
CONF_TITLE = "title"
CONF_TARGETS = "targets"
CONF_DATA = "data"
CONF_TARGET_DATA = "target_data"
CONF_PRIORITY = "priority"
CONF_SKIP_GREETING = "skip_greeting"
CONF_OVERRIDE_GREETINGS = "override_greetings"

# --- Chiavi Canale Singolo ---
CONF_SERVICE = "service"
CONF_TARGET = "target"
CONF_ENTITY_ID = "entity_id"
CONF_IS_VOICE = "is_voice"
CONF_ALT_SERVICES = "alt_services"
CONF_TYPE = "type"

# --- Piattaforme HA ---
PLATFORMS = ["sensor", "binary_sensor", "select", "number"]


def get_device_info(entry_id: str):
    """Device info condiviso da tutte le entità."""
    from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name="Universal Notifier",
        manufacturer="Universal Notifier",
        entry_type=DeviceEntryType.SERVICE,
    )

# --- Companion App Commands ---
COMPANION_COMMANDS = [
    "TTS",
    "request_location_update",
    "clear_badge",
    "ble_write",
    "close_notifications",
    "clear_notification",
    "remove_channel",
    "stop_tts",
    "app_launch",
    "update_sensors",
]
