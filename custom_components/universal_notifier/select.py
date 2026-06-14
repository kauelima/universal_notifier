# /config/custom_components/universal_notifier/select.py
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN, CONF_PRIORITY_VOLUME, get_device_info

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        PriorityVolumeSelect(hass, entry),
        TextFormatSelect(hass, entry),
        NotificationModeSelect(hass, entry),
    ], True)

class PriorityVolumeSelect(SelectEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Priority Volume"

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_priority_volume"
        self._attr_options = [str(round(i/10, 1)) for i in range(1, 11)]
        conf = hass.data[DOMAIN][entry.entry_id]["conf"]
        self._attr_current_option = str(conf.get(CONF_PRIORITY_VOLUME, 0.9))
        self._attr_device_info = get_device_info(entry.entry_id)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            self._attr_current_option = last_state.state
        self.hass.data[DOMAIN][self._entry_id]["runtime_priority_vol"] = float(self._attr_current_option)

    async def async_select_option(self, option: str) -> None:
        self.hass.data[DOMAIN][self._entry_id]["runtime_priority_vol"] = float(option)
        self._attr_current_option = option
        self.async_write_ha_state()


class TextFormatSelect(SelectEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Text Format"
    _attr_options = ["html", "markdown", "markdownv2", "plain_text"]
    _attr_icon = "mdi:format-text"

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_text_format"
        self._attr_current_option = "html"
        self._attr_device_info = get_device_info(entry.entry_id)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            self._attr_current_option = last_state.state
        self.hass.data[DOMAIN][self._entry_id]["text_format"] = self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        self.hass.data[DOMAIN][self._entry_id]["text_format"] = option
        self._attr_current_option = option
        self.async_write_ha_state()


class NotificationModeSelect(SelectEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Notification Mode"
    _attr_options = ["Normal", "Voice home", "Text home"]
    _attr_icon = "mdi:home-sound-out"

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_notification_mode"
        self._attr_current_option = "Normal"
        self._attr_device_info = get_device_info(entry.entry_id)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            self._attr_current_option = last_state.state
        self.hass.data[DOMAIN][self._entry_id]["notification_mode"] = self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        self.hass.data[DOMAIN][self._entry_id]["notification_mode"] = option
        self._attr_current_option = option
        self.async_write_ha_state()