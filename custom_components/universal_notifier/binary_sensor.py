# /config/custom_components/universal_notifier/binary_sensor.py
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.util import dt as dt_util
from .const import DOMAIN, CONF_DND, ENTITY_DND_OVERRIDE, get_device_info
from homeassistant.helpers import entity_registry as er
from .utils import is_time_in_range

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    conf = hass.data[DOMAIN][entry.entry_id]["conf"]
    async_add_entities([UNotifierDNDSensor(conf, entry)], True)

class UNotifierDNDSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "DND"

    def __init__(self, conf, entry):
        dnd = conf.get(CONF_DND, {})
        # Retrocompat: migrate old flat DND to nested weekday/weekend
        if isinstance(dnd, dict) and "weekday" not in dnd and "start" in dnd:
            dnd = {"weekday": dnd, "weekend": dnd}
        self._dnd = dnd
        self._weekend_days = [int(d) if isinstance(d, str) else d for d in conf.get("weekend_days", ["5", "6"])]
        self._dnd_override_uid = f"{DOMAIN}_{entry.entry_id}_{ENTITY_DND_OVERRIDE}"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_dnd"
        self._attr_device_info = get_device_info(entry.entry_id)

    @property
    def is_on(self) -> bool:
        """Ritorna True se DND è attivo."""
        if not self._dnd: return False
        now = dt_util.now()
        now_time = now.time()
        now_weekday = now.weekday()
        if now_weekday in self._weekend_days:
            active_dnd = self._dnd.get("weekend", self._dnd.get("weekday", {"start": "23:00", "end": "06:00"}))
        else:
            active_dnd = self._dnd.get("weekday", {"start": "23:00", "end": "06:00"})
        time_dnd_active = is_time_in_range(active_dnd["start"], active_dnd["end"], now_time)

        # DND Override: switch entity forces DND on
        ent_reg = er.async_get(self.hass)
        dnd_override_entry = ent_reg.async_get_entity_id("switch", DOMAIN, self._dnd_override_uid)
        dnd_state = self.hass.states.get(dnd_override_entry) if dnd_override_entry else None
        if dnd_state and dnd_state.state == "on":
            return True
        return time_dnd_active

    @property
    def icon(self):
        """Icona dinamica: bell-off se DND è attivo (silenzioso)."""
        return "mdi:bell-off" if self.is_on else "mdi:bell-on"