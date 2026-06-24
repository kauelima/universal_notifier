# /config/custom_components/universal_notifier/switch.py
"""Switch entity for Universal Notifier — DND override toggle."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN, ENTITY_DND_OVERRIDE, get_device_info


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([UNotifierDNDOverrideSwitch(entry)])


class UNotifierDNDOverrideSwitch(SwitchEntity):
    """Switch that forces DND on when enabled, overriding time-based DND."""

    _attr_has_entity_name = True
    _attr_name = "DND Override"
    _attr_is_on = False

    def __init__(self, entry):
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{ENTITY_DND_OVERRIDE}"
        self._attr_device_info = get_device_info(entry.entry_id)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def icon(self) -> str:
        return "mdi:bell-sleep" if self.is_on else "mdi:bell"
