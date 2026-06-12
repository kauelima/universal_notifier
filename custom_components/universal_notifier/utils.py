# /config/custom_components/universal_notifier/binary_sensor.py
import re
from homeassistant.util import dt as dt_util

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def estimate_tts_duration(text: str, buffer: float = 1.5) -> float:
    """Stima la durata del messaggio in secondi basandosi sulle parole."""
    if not text: return 0
    # Media: 2.5 parole al secondo circa (o 150 parole/minuto)
    words = len(text.split())
    estimated_seconds = (words / 2.5) + buffer
    return max(buffer + 2.0, estimated_seconds)

def is_time_in_range(start_str: str, end_str: str, now_time) -> bool:
    """Controlla se l'orario attuale è in un range (gestisce accavallamento della notte)."""
    start = dt_util.parse_time(start_str)
    end = dt_util.parse_time(end_str)
    if start <= end:
        return start <= now_time <= end
    else:
        return start <= now_time or now_time <= end

def get_current_slot_info(slots_conf: dict, now_time,
                          now_weekday: int = None,
                          weekend_days: list = None) -> tuple:
    """Restituisce (nome_slot, volume) basandosi sull'ora attuale e giorno."""
    # Se la config è vuota, usiamo i default
    if not slots_conf:
        slots_conf = DEFAULT_TIME_SLOTS

    # Determine which group to use: weekend vs weekday
    # Convert weekend_days to ints (HA selector now returns strings)
    if weekend_days is not None:
        weekend_days = [int(d) if isinstance(d, str) else d for d in weekend_days]
    if (weekend_days is not None and now_weekday is not None
            and now_weekday in weekend_days):
        group = slots_conf.get("weekend", slots_conf)
    else:
        group = slots_conf.get("weekday", slots_conf)

    # If the selected group is itself flat (old format or fallback),
    # "weekday" / "weekend" key won't exist, so group = slots_conf (flat dict).
    # If group is a nested dict with slot keys, use it; otherwise fall back.
    if not group or not isinstance(group, dict):
        group = slots_conf

    # Check if group is flat (old format: {"morning": {...}, ...})
    # vs nested (new format). If the first value is a dict with "start", it's flat.
    sample_val = next(iter(group.values()), None)
    if isinstance(sample_val, dict) and "start" in sample_val:
        working_slots = group
    else:
        # Fallback: use the original slots_conf directly (old flat format)
        working_slots = slots_conf

    sorted_slots = []
    for name, data in working_slots.items():
        if not isinstance(data, dict):
            continue
        t_str = data.get("start")
        t_obj = dt_util.parse_time(t_str) if t_str else None
        vol_val = data.get("volume", 0.2)
        if t_obj:
            sorted_slots.append((name, t_obj, vol_val))
    # Ordina per orario di inizio
    sorted_slots.sort(key=lambda x: x[1])
    if not sorted_slots:
        return "default", 0.2
    # Logica: Inizializziamo con l'ultimo slot della lista.
    # Questo copre il caso "notte" (es. dalle 23:00 alle 07:00).
    current_slot = sorted_slots[-1][0]
    current_vol = sorted_slots[-1][2]
    for name, start_time, vol_val in sorted_slots:
        if now_time >= start_time:
            current_slot = name
            current_vol = vol_val
    return current_slot, current_vol

def clean_text_for_tts(text: str) -> str:
    """Rimuove caratteri speciali per la sintesi vocale."""
    if not text: return ""
    text = re.sub(r'[*_`\[\]]', '', text) # Via markdown
    text = re.sub(r'http\S+', '', text)    # Via URL
    return text.strip()

def sanitize_text_visual(text: str, parse_mode: str = None) -> str:
    """Pulisce o esegue l'escape del testo per visualizzazione (HTML/Markdown)."""
    if not text: return ""
    if parse_mode and "html" in parse_mode.lower():
        text = text.replace("<", "&lt;").replace(">", "&gt;")
    return text

def apply_formatting(text: str, parse_mode: str, style: str = "bold") -> str:
    """Applica la formattazione (grassetto) in base al parse_mode."""
    if not text: return ""
    mode = parse_mode.lower() if parse_mode else ""
    if "html" in mode:
        if style == "bold": return f"<b>{text}</b>"
    elif "markdown" in mode:
        return f"**{text}**" 
    return text