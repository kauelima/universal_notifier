# /config/custom_components/universal_notifier/text.py
"""Text entity for Universal Notifier — stores the last sent message."""
from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from .const import DOMAIN, ENTITY_LAST_MESSAGE, get_device_info


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([UNotifierLastMessageText(entry)])


class UNotifierLastMessageText(TextEntity):
    """Text entity that stores the last message sent by the notifier."""

    _attr_has_entity_name = True
    _attr_name = "Last Message Sent"
    _attr_native_min = 0
    _attr_native_max = 255
    _attr_mode = TextMode.TEXT
    _attr_native_value = ""

    def __init__(self, entry):
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{ENTITY_LAST_MESSAGE}"
        self._attr_device_info = get_device_info(entry.entry_id)

    async def async_set_value(self, value: str) -> None:
        """Called by the text.set_value service."""
        self._attr_native_value = value[:255] if value else ""
        self.async_write_ha_state()

    @property
    def icon(self) -> str:
        return "mdi:message-text"
