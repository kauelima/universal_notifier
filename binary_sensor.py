# /config/custom_components/universal_notifier/binary_sensor.py
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.util import dt as dt_util
from .const import DOMAIN, CONF_DND, get_device_info
from .utils import is_time_in_range

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    conf = hass.data[DOMAIN][entry.entry_id]["conf"]
    async_add_entities([UNotifierDNDSensor(conf, entry)], True)

class UNotifierDNDSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "DND"

    def __init__(self, conf, entry):
        self._conf = conf.get(CONF_DND, {})
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_dnd"
        self._attr_device_info = get_device_info(entry.entry_id)

    @property
    def is_on(self) -> bool:
        """Ritorna True se DND è attivo."""
        if not self._conf: return False
        now_time = dt_util.now().time()
        return is_time_in_range(self._conf["start"], self._conf["end"], now_time)

    @property
    def icon(self):
        """Icona dinamica: bell-off se DND è attivo (silenzioso)."""
        return "mdi:bell-off" if self.is_on else "mdi:bell-on"