# /config/custom_components/universal_notifier/__init__.py

import logging
import random
import re
import asyncio
import math
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import ATTR_ENTITY_ID, STATE_PLAYING, CONF_SERVICE, CONF_TYPE
from homeassistant.util import dt as dt_util
from homeassistant.config_entries import ConfigEntry
####
from .utils import *
from .const import (
    DOMAIN,
    PLATFORMS,
    # Config keys
    CONF_CHANNELS, CONF_ASSISTANT_NAME, CONF_DATE_FORMAT,
    CONF_GREETINGS, CONF_TIME_SLOTS, CONF_DND, CONF_BOLD_PREFIX,
    # Service keys (Inputs)
    CONF_MESSAGE, CONF_TITLE, CONF_TARGETS, CONF_DATA, CONF_TARGET_DATA,
    CONF_PRIORITY, CONF_SKIP_GREETING, CONF_INCLUDE_TIME, CONF_PRIORITY_VOLUME, CONF_OVERRIDE_GREETINGS,
    CONF_PERSON_ENTITIES,
    # Inner Channel keys
    CONF_SERVICE, CONF_TARGET, CONF_ENTITY_ID,
    CONF_IS_VOICE, CONF_ALT_SERVICES, CONF_TYPE,
    # Other
    COMPANION_COMMANDS,
)

_LOGGER = logging.getLogger(__name__)
# Dizionario globale per tracciare gli stati originali fuori dal worker
_ORIGINAL_STATES = {}


# ==============================================================================
# LOGICA DI RICARICA E SCARICO
# ==============================================================================
async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Ricarica l'entry quando le opzioni vengono aggiornate dall'utente."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Scarica l'entry e libera le risorse."""
    # Pulizia stati snapshot eventualmente orfani
    _ORIGINAL_STATES.clear()

    # Rimuovi il servizio
    hass.services.async_remove(DOMAIN, "send")

    # Scarica le piattaforme
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok

# ==============================================================================
# LOGICA DI RESUME
# ==============================================================================

async def _get_player_snapshot(hass: HomeAssistant, entity_id: str) -> dict:
    """Cattura lo stato originale SOLO se non siamo già in una sessione di notifica."""
    if entity_id in _ORIGINAL_STATES:
        _LOGGER.debug(f"UniNotifier: {entity_id} già in sessione, salto snapshot.")
        return None
    state = hass.states.get(entity_id)
    if not state: return None
    attr = state.attributes
    snap = {
        "state": state.state,
        "volume": attr.get("volume_level"),
        "app_name": attr.get("app_name"),
        "media_content_id": attr.get("media_content_id"),
        "media_content_type": attr.get("media_content_type"),
        "media_position": attr.get("media_position"),
        "entity_id": entity_id
    }
    _ORIGINAL_STATES[entity_id] = snap
    _LOGGER.debug(f"UniNotifier: Snapshot originale salvato per {entity_id}: {snap}")
    return snap

async def _apply_resume(hass: HomeAssistant, entity_id: str, target_volume: float):
    """Ripristina lo stato salvato all'inizio della sessione."""
    snap = _ORIGINAL_STATES.pop(entity_id, None)
    if not snap:
        await hass.services.async_call("media_player", "volume_set", {
            "entity_id": entity_id, "volume_level": target_volume
        })
        return
    # 1. Ripristino Volume
    if snap["volume"] is not None:
        await hass.services.async_call("media_player", "volume_set", {
            "entity_id": entity_id, "volume_level": snap["volume"]
        })
    _LOGGER.debug(f"UniNotifier: Resume del volume di {entity_id} con {snap['volume']}")
    # 2. Ripristino Contenuto (solo se stava suonando prima della prima notifica)
    if snap["state"] == STATE_PLAYING:
        app = (snap.get("app_name") or "").lower()
        c_id = snap.get("media_content_id")
        try:
            if "spotify" in app or (c_id and "spotify" in c_id):
                await hass.services.async_call("media_player", "play_media", {
                    "entity_id": entity_id, "media_content_id": c_id, "media_content_type": "music"
                })
            else:
                await hass.services.async_call("media_player", "play_media", {
                    "entity_id": entity_id, "media_content_id": c_id,
                    "media_content_type": snap.get("media_content_type", "audio/mpeg")
                })
            _LOGGER.debug(f"UniNotifier: Tentativo di resume eseguito per {entity_id}")
        except Exception as e:
            _LOGGER.error(f"UniNotifier: Errore nel resume di {entity_id}: {e}")

# ==============================================================================
# SERVICE SCHEMA
# ==============================================================================

SEND_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_MESSAGE): cv.string,
    vol.Required(CONF_TARGETS): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_TITLE): cv.string,
    vol.Optional(CONF_DATA): dict,
    vol.Optional(CONF_TARGET_DATA): dict,
    vol.Optional(CONF_PRIORITY): cv.boolean,
    vol.Optional(CONF_SKIP_GREETING): cv.boolean,
    vol.Optional(CONF_INCLUDE_TIME): cv.boolean,
    vol.Optional(CONF_PRIORITY_VOLUME): cv.string,
    vol.Optional(CONF_ASSISTANT_NAME): cv.string,
    vol.Optional(CONF_BOLD_PREFIX): cv.boolean,
    vol.Optional(CONF_OVERRIDE_GREETINGS): dict,
}, extra=vol.ALLOW_EXTRA)

# ==============================================================================
# CONFIG ENTRY SETUP
# ==============================================================================

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup del componente Universal Notifier da config entry (UI)."""

    # Config effettiva: options sovrascrivono data (merge shallow)
    conf = {**entry.data, **entry.options}

    # --- Estrazione variabili di configurazione ---
    channels_config     = conf.get(CONF_CHANNELS, {})
    global_name         = conf.get(CONF_ASSISTANT_NAME, "")
    global_date_fmt     = conf.get(CONF_DATE_FORMAT, "%H:%M:%S")
    global_include_time = conf.get(CONF_INCLUDE_TIME, True)
    global_priority_vol = conf.get(CONF_PRIORITY_VOLUME, 0.9)
    time_slots_conf     = conf.get(CONF_TIME_SLOTS, {})
    dnd_conf            = conf.get(CONF_DND, {"start": "23:00", "end": "06:00"})
    base_greetings      = conf.get(CONF_GREETINGS, {})
    global_bold_setting = conf.get(CONF_BOLD_PREFIX, True)

    # --- Inizializzazione coda TTS ---
    voice_queue = asyncio.Queue()

    person_entities_conf = conf.get(CONF_PERSON_ENTITIES, [])

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "conf":               conf,
        "voice_queue":        voice_queue,
        "runtime_priority_vol": None,   # override runtime da select entity
        "tts_buffer":         1.5,      # sovrascrivibile da number entity
        "text_format":        "html",   # sovrascrivibile da select entity
        "notification_mode":  "Normal", # sovrascrivibile da select entity
    }

    ############################################################################
    async def voice_queue_worker():
        """Lavoratore in background che consuma la coda vocale."""
        _LOGGER.debug("UniNotifier: Voice Queue Worker avviato.")
        while True:
            task = await voice_queue.get()
            try:
                players = task['physical_players']
                target_vol = task['target_volume']
                # 1. SNAPSHOT (Solo all'inizio della catena)
                for eid in players:
                    await _get_player_snapshot(hass, eid)
                # 2. IMPOSTA VOLUME TARGET
                if players and target_vol is not None:
                    await hass.services.async_call("media_player", "volume_set", {
                        "entity_id": players, "volume_level": target_vol
                    })
                # 3. ESECUZIONE NOTIFICA
                _LOGGER.debug(f"UniNotifier: Elaborazione messaggio vocale: {task['text_content'][:35]}...")
                _LOGGER.debug(f"UniNotifier: {task['physical_players']} {task['target_volume']} {task['service']} {task['payload']} ")
                await hass.services.async_call(task['domain'], task['service'], task['payload'])
                # 4. ATTESA FINE MESSAGGIO
                tts_buffer = hass.data[DOMAIN][entry.entry_id].get("tts_buffer", 1.5)
                wait_time = estimate_tts_duration(task['text_content'], buffer=tts_buffer)
                _LOGGER.debug(f"UniNotifier: Attesa di {wait_time:.2f}s per fine messaggio.")
                await asyncio.sleep(wait_time)
                # 5. CONTROLLO CODA PER RESUME
                if voice_queue.empty():
                    _LOGGER.debug("UniNotifier: Coda vuota, chiusura sessione e ripristino media.")
                    for eid in list(_ORIGINAL_STATES.keys()):
                        await _apply_resume(hass, eid, target_vol)
                else:
                    _LOGGER.debug(f"UniNotifier: Coda non vuota ({voice_queue.qsize()} messaggi), posticipo resume.")
            except Exception as e:
                _ORIGINAL_STATES.clear()
                _LOGGER.error(f"UniNotifier: Errore nel worker vocale: {e}")
            finally:
                voice_queue.task_done()

    worker_task = hass.loop.create_task(voice_queue_worker())

    # Cancella il worker quando l'entry viene scaricata (reload/rimozione)
    def _cancel_worker() -> None:
        worker_task.cancel()

    entry.async_on_unload(_cancel_worker)

    ############################################################################
    async def async_send_notification(call: ServiceCall):
        """Handler principale del servizio 'send'."""
        # 1. Parsing Input
        global_raw_message = call.data.get(CONF_MESSAGE, "")
        global_title = call.data.get(CONF_TITLE)
        runtime_data = call.data.get(CONF_DATA, {})
        target_specific_data = call.data.get(CONF_TARGET_DATA, {})
        targets = call.data.get(CONF_TARGETS, [])
        override_name = call.data.get(CONF_ASSISTANT_NAME, global_name)
        skip_greeting = call.data.get(CONF_SKIP_GREETING, False)
        include_time = call.data.get(CONF_INCLUDE_TIME, global_include_time)
        # priority_volume: prima controlla override runtime (select entity), poi call data, poi config
        runtime_pv = hass.data[DOMAIN][entry.entry_id].get("runtime_priority_vol")
        priority_volume = call.data.get(
            CONF_PRIORITY_VOLUME,
            runtime_pv if runtime_pv is not None else float(global_priority_vol)
        )
        is_priority = call.data.get(CONF_PRIORITY, False)
        use_bold_prefix = call.data.get(CONF_BOLD_PREFIX, global_bold_setting)

        # 2. Analisi Contesto
        now = dt_util.now()
        now_time = now.time()
        slot_key, slot_volume = get_current_slot_info(time_slots_conf, now_time)
        is_dnd_active = is_time_in_range(dnd_conf["start"], dnd_conf["end"], now_time)

        # 3. Gestione Saluti
        override_greetings_data = call.data.get(CONF_OVERRIDE_GREETINGS)
        effective_greetings = base_greetings
        if override_greetings_data:
            effective_greetings = base_greetings.copy()
            for key, value in override_greetings_data.items():
                if key in effective_greetings:
                    if not isinstance(value, list): value = [value]
                    effective_greetings[key] = value

        options = effective_greetings.get(slot_key, [])
        current_greeting = random.choice(options) if options and not skip_greeting else ""
        raw_name = override_name
        raw_time_str = now.strftime(global_date_fmt) if include_time else ""
        if isinstance(targets, str): targets = [targets]

        tasks = []

        # ======================================================================
        # 4. CICLO SUI CANALI
        # ======================================================================
        for target_alias in targets:
            if target_alias not in channels_config:
                _LOGGER.debug(f"UniNotifier: Target '{target_alias}' sconosciuto.")
                continue
            channel_conf = channels_config[target_alias]
            _LOGGER.debug(f"UniNotifier: Channel Configuration {channel_conf}")

            ####################################################################
            # A. Preparazione Dati Specifici
            specific_data = {}
            if target_alias in target_specific_data:
                specific_data = target_specific_data[target_alias].copy()
            _LOGGER.debug(f"UniNotifier: Specific Data {specific_data}")
            target_raw_message = specific_data.pop(CONF_MESSAGE, global_raw_message)

            dynamic_entities = specific_data.pop(CONF_ENTITY_ID, channel_conf.get(CONF_TARGET))
            if isinstance(dynamic_entities, str): dynamic_entities = [dynamic_entities]
            elif dynamic_entities is None: dynamic_entities = []
            _LOGGER.debug(f"UniNotifier: Dynamic Entities {dynamic_entities}")

            ####################################################################
            # B. Selezione Servizio
            service_type = specific_data.pop(CONF_TYPE, runtime_data.get(CONF_TYPE, None))
            alt_services_conf = channel_conf.get(CONF_ALT_SERVICES, {})
            _LOGGER.debug(f"UniNotifier: Service type {service_type}")
            _LOGGER.debug(f"UniNotifier: Service alt {alt_services_conf}")

            if service_type and service_type in alt_services_conf:
                target_service_conf = alt_services_conf[service_type]
                full_service_name = target_service_conf[CONF_SERVICE]
                is_voice_channel = False
            else:
                full_service_name = channel_conf[CONF_SERVICE]
                is_voice_channel = channel_conf.get(CONF_IS_VOICE, False)
            _LOGGER.debug(f"UniNotifier: Full Service Name {full_service_name}")

            try:
                srv_domain, srv_name = full_service_name.split(".", 1)
            except ValueError:
                _LOGGER.error(f"UniNotifier: Servizio non valido {full_service_name}")
                continue

            ####################################################################
            # C. Check Comandi MOBILE APP
            is_command_message = False
            if target_raw_message in COMPANION_COMMANDS or str(target_raw_message).startswith("command_"):
                is_command_message = True

            ####################################################################
            # D. COSTRUZIONE MESSAGGIO E TITOLO
            parse_mode = specific_data.get("parse_mode", runtime_data.get("parse_mode"))
            if not parse_mode and not is_voice_channel:
                parse_mode = hass.data[DOMAIN][entry.entry_id].get("text_format", "html")
            final_msg = ""
            final_title = global_title
            text_content_for_duration = ""
            if is_command_message:
                final_msg = target_raw_message
            else:
                if is_voice_channel:
                    clean_msg = clean_text_for_tts(str(target_raw_message))
                    clean_greet = clean_text_for_tts(current_greeting)
                    full_spoken_text = ""
                    if final_title:
                        clean_title = clean_text_for_tts(final_title)
                        if clean_title:
                            full_spoken_text += f"{clean_title}. "
                    if clean_greet:
                        full_spoken_text += f"{clean_greet}. "
                    full_spoken_text += clean_msg
                    final_msg = full_spoken_text
                    final_title = None
                    text_content_for_duration = final_msg
                else:
                    clean_name = sanitize_text_visual(raw_name, parse_mode)
                    clean_time = sanitize_text_visual(raw_time_str, parse_mode)
                    clean_msg = sanitize_text_visual(str(target_raw_message), parse_mode)
                    clean_greet = sanitize_text_visual(current_greeting, parse_mode)
                    clean_orig_title = sanitize_text_visual(final_title, parse_mode) if final_title else None
                    if use_bold_prefix:
                        clean_name = apply_formatting(clean_name, parse_mode, "bold")
                        clean_time = apply_formatting(clean_time, parse_mode, "bold")
                        clean_orig_title = apply_formatting(clean_orig_title, parse_mode, "bold")
                    prefix_content = clean_name
                    if clean_time:
                        prefix_content += f" - {clean_time}"
                    clean_prefix = f"[{prefix_content}]"
                    greeting_part = f"{clean_greet}. " if clean_greet else ""
                    if clean_orig_title:
                        final_title = f"{clean_prefix} {clean_orig_title}"
                        final_msg = f"{greeting_part}{clean_msg}"
                    else:
                        final_msg = f"{clean_prefix} {greeting_part}{clean_msg}"

            ####################################################################
            # E. Determinazione del Volume attuale
            override_volume = specific_data.get("volume", runtime_data.get("volume"))
            if override_volume is not None:
                try: target_volume = float(override_volume)
                except ValueError: target_volume = slot_volume
            elif is_priority:
                target_volume = priority_volume
            else:
                target_volume = slot_volume

            ####################################################################
            # F. Applicazione Volume e Check DND (Solo Canali Voce)
            if is_voice_channel:
                if is_dnd_active and not is_priority and override_volume is None:
                    _LOGGER.debug(f"UniNotifier: Skipped '{target_alias}' (DND attivo)")
                    continue

            ####################################################################
            # F2. Filtro routing in base a notification_mode
            # Attivo SOLO se ci sono person entities configurate
            notification_mode = hass.data[DOMAIN][entry.entry_id].get("notification_mode", "Normal")
            if person_entities_conf and notification_mode != "Normal":
                if notification_mode == "Voice home":
                    family_state = hass.states.get(f"sensor.{DOMAIN}_family")
                    family_home = family_state is not None and family_state.state == "home"
                    if family_home and not is_voice_channel:
                        _LOGGER.debug(f"UniNotifier: Skipped '{target_alias}' (Voice home, family a casa → solo voce)")
                        continue
                    elif not family_home and is_voice_channel:
                        _LOGGER.debug(f"UniNotifier: Skipped '{target_alias}' (Voice home, family non a casa → solo testo)")
                        continue
                elif notification_mode == "Text home":
                    if is_voice_channel:
                        _LOGGER.debug(f"UniNotifier: Skipped '{target_alias}' (Text home mode)")
                        continue

            ####################################################################
            # G. Costruzione Payload Finale
            service_payload = {}
            _LOGGER.debug(f"UniNotifier: final_title '{final_title}' ")
            if srv_domain == "telegram_bot":
                if "parse_mode" not in service_payload and parse_mode:
                    service_payload["parse_mode"] = parse_mode
                if service_type in ["photo", "video", "animation", "voice", "document"]:
                    service_payload["caption"] = final_msg
                else:
                    service_payload["message"] = final_msg
            else:
                service_payload["message"] = final_msg
            if final_title:
                service_payload["title"] = final_title
                if service_type in ["photo", "video", "animation", "voice", "document"]:
                    service_payload["caption"] = final_title + " " + final_msg
                    service_payload.pop("title", None)

            ####################################################################
            # H. Routing dei Target nel Payload
            conf_target_value = channel_conf.get(CONF_TARGET)
            if conf_target_value:
                if srv_domain == "tts":
                    service_payload[ATTR_ENTITY_ID] = conf_target_value
                else:
                    service_payload[CONF_TARGET] = conf_target_value

            ####################################################################
            # I. Merge Dati Accessori (alexa type, telegram images, etc.)
            all_additional_data = {}
            if runtime_data: all_additional_data.update(runtime_data)
            if specific_data: all_additional_data.update(specific_data)
            for k in ["volume", CONF_TYPE, "parse_mode"]: all_additional_data.pop(k, None)

            if all_additional_data:
                if srv_domain == "notify":
                    if "data" not in service_payload: service_payload["data"] = {}
                    service_payload["data"].update(all_additional_data)
                else:
                    service_payload.update(all_additional_data)

            ####################################################################
            physical_players = []
            # J. DISPATCH LOGIC: CODA PER VOCE vs IMMEDIATO
            if srv_domain == "telegram_bot":
                p = service_payload.copy()
                notify_targets = channel_conf.get(CONF_TARGET, [])
                if isinstance(notify_targets, str): notify_targets = [notify_targets]
                p[CONF_TARGET] = str(notify_targets[0])
                _LOGGER.debug(f"UniNotifier: Final payload {p} - Service data {srv_domain}/{srv_name}")
                tasks.append(hass.services.async_call(srv_domain, srv_name, p))

            elif is_voice_channel:
                if srv_domain == "tts":
                    if dynamic_entities:
                        service_payload["media_player_entity_id"] = dynamic_entities
                        tts_entities = service_payload.get("media_player_entity_id", [])
                        if isinstance(tts_entities, str):
                            physical_players.append(tts_entities)
                        else:
                            physical_players.extend(tts_entities)
                elif srv_domain == "notify":
                    notify_targets = ""
                    if dynamic_entities:
                        notify_targets = dynamic_entities
                    else:
                        notify_targets = channel_conf.get(CONF_TARGET, [])
                    if isinstance(notify_targets, str):
                        physical_players.append(notify_targets)
                    else:
                        physical_players.extend(notify_targets)
                physical_players = [p for p in physical_players if isinstance(p, str) and p.startswith("media_player.")]
                _LOGGER.debug(f"UniNotifier: Media players coinvolti {physical_players}.")
                queue_item = {
                    'domain': srv_domain,
                    'service': srv_name,
                    'payload': service_payload,
                    'text_content': text_content_for_duration,
                    'physical_players': physical_players,
                    'target_volume': target_volume
                }
                voice_queue.put_nowait(queue_item)
                _LOGGER.debug(f"UniNotifier: Messaggio per {target_alias} accodato.")
            else:
                _LOGGER.debug(f"UniNotifier: Final payload {service_payload} - Service data {srv_domain}/{srv_name}")
                tasks.append(hass.services.async_call(srv_domain, srv_name, service_payload))

        if tasks:
            await asyncio.gather(*tasks)

    ############################################################################
    # Registrazione servizio e caricamento piattaforme
    hass.services.async_register(DOMAIN, "send", async_send_notification, schema=SEND_SERVICE_SCHEMA)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Ricarica l'entry quando l'utente salva le opzioni
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True