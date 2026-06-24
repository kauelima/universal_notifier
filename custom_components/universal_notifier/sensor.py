# /config/custom_components/universal_notifier/sensor.py
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import (CONF_CHANNELS, CONF_DEFAULT_MEDIA_PLAYER, CONF_IS_VOICE,
                    CONF_PERSON_ENTITIES, CONF_TIME_SLOTS, DOMAIN,
                    get_device_info)
from .utils import get_current_slot_info


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    conf = hass.data[DOMAIN][entry.entry_id]["conf"]
    async_add_entities([
        UNotifierVolumeSensor(conf, entry),
        UNotifierFamilySensor(hass, conf, entry),
        UNotifierDefaultPlayerSensor(conf, entry),
    ], True)

class UNotifierVolumeSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Volume"

    def __init__(self, conf, entry):
        self._slots = conf.get(CONF_TIME_SLOTS, {})
        self._weekend_days = conf.get("weekend_days", ["5", "6"])
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_volume"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_info = get_device_info(entry.entry_id)

    @property
    def native_value(self):
        """Volume calcolato in percentuale (0-100)."""
        now = dt_util.now()
        now_time = now.time()
        now_weekday = now.weekday()
        _, vol = get_current_slot_info(self._slots, now_time, now_weekday, self._weekend_days)
        return int(vol * 100)

    @property
    def icon(self):
        """Cambia l'icona in base al livello del volume."""
        vol = self.native_value
        if vol == 0:
            return "mdi:volume-mute"
        if vol < 34:
            return "mdi:volume-low"
        if vol < 67:
            return "mdi:volume-medium"
        return "mdi:volume-high"

    @property
    def extra_state_attributes(self):
        now = dt_util.now()
        now_time = now.time()
        now_weekday = now.weekday()
        slot_name, vol = get_current_slot_info(self._slots, now_time, now_weekday, self._weekend_days)
        return {
            "current_slot": slot_name,
            "raw_volume": vol
        }


class UNotifierFamilySensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Family"
    _attr_icon = "mdi:home-account"

    def __init__(self, hass, conf, entry):
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_family"
        self._person_entities = conf.get(CONF_PERSON_ENTITIES, [])
        self._attr_device_info = get_device_info(entry.entry_id)

    @property
    def native_value(self) -> str:
        for entity_id in self._person_entities:
            state = self.hass.states.get(entity_id)
            if state and state.state == "home":
                return "home"
        return "not_home"

    async def async_added_to_hass(self):
        if self._person_entities:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, self._person_entities, self._handle_change
                )
            )

    @callback
    def _handle_change(self, event):
        self.async_write_ha_state()


class UNotifierDefaultPlayerSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Default Media Players"
    _attr_icon = "mdi:speaker-multiple"

    def __init__(self, conf, entry):
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_default_players"
        self._attr_device_info = get_device_info(entry.entry_id)
        channels = conf.get(CONF_CHANNELS, {})
        self._voice_defaults = {
            alias: ch.get(CONF_DEFAULT_MEDIA_PLAYER, "")
            for alias, ch in channels.items()
            if ch.get(CONF_IS_VOICE, False) and ch.get(CONF_DEFAULT_MEDIA_PLAYER, "")
        }

    @property
    def native_value(self):
        return len(self._voice_defaults)

    @property
    def extra_state_attributes(self):
        return self._voice_defaults