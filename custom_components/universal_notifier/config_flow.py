"""Config flow for Universal Notifier."""
from __future__ import annotations

import json
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.util import dt as dt_util
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .const import DOMAIN, CONF_PERSON_ENTITIES

# ---------------------------------------------------------------------------
# Slot keys (ordine fisso)
# ---------------------------------------------------------------------------
SLOT_KEYS = ["morning", "afternoon", "evening", "night"]

# ---------------------------------------------------------------------------
# Default values (qui e non in const.py, perché usati solo nel config flow)
# ---------------------------------------------------------------------------
DEFAULT_ASSISTANT_NAME  = ""
DEFAULT_DATE_FORMAT     = "%H:%M:%S"
DEFAULT_INCLUDE_TIME    = True
DEFAULT_BOLD_PREFIX     = True
DEFAULT_PRIORITY_VOLUME = 0.9
DEFAULT_DND             = {"start": "23:00", "end": "06:00"}
DEFAULT_TIME_SLOTS      = {
    "morning":   {"start": "07:00", "volume": 0.35},
    "afternoon": {"start": "12:00", "volume": 0.40},
    "evening":   {"start": "19:00", "volume": 0.30},
    "night":     {"start": "22:00", "volume": 0.10},
}
DEFAULT_GREETINGS = {
    "morning":   ["Buongiorno", "Ben alzato", "Salve", "Buondì"],
    "afternoon": ["Buon pomeriggio", "Ciao", "Ben ritrovato"],
    "evening":   ["Buonasera", "Buona serata", "Ben tornato a casa"],
    "night":     ["Buonanotte", "Sogni d'oro", "È tardi"],
}

# ---------------------------------------------------------------------------
# Selector helpers
# ---------------------------------------------------------------------------
_SLIDER_0_1    = NumberSelector(
    NumberSelectorConfig(min=0.0, max=1.0, step=0.05, mode=NumberSelectorMode.SLIDER)
)
_TEXT          = TextSelector()
_BOOL          = BooleanSelector()
_MULTILINE     = TextSelector(TextSelectorConfig(multiline=True))
_PERSON_MULTI  = EntitySelector(EntitySelectorConfig(domain="person", multiple=True))


def _is_valid_time(value: str) -> bool:
    """Return True if value is a valid HH:MM time string."""
    return bool(value and dt_util.parse_time(value) is not None)


def _greetings_to_text(greetings: dict) -> dict[str, str]:
    """Convert {slot: [str, ...]} → {slot_greetings: "str\nstr"} for form pre-fill."""
    return {
        f"{slot}_greetings": "\n".join(greetings.get(slot, []))
        for slot in SLOT_KEYS
    }


def _text_to_greetings(user_input: dict) -> dict[str, list[str]]:
    """Convert form fields back to {slot: [str, ...]}."""
    return {
        slot: [
            line.strip()
            for line in user_input.get(f"{slot}_greetings", "").split("\n")
            if line.strip()
        ]
        for slot in SLOT_KEYS
    }


def _slots_to_fields(ts: dict) -> dict:
    """Convert time_slots dict to flat form fields for pre-fill."""
    fields = {}
    for slot in SLOT_KEYS:
        fields[f"{slot}_start"]  = ts.get(slot, DEFAULT_TIME_SLOTS[slot])["start"]
        fields[f"{slot}_volume"] = ts.get(slot, DEFAULT_TIME_SLOTS[slot])["volume"]
    return fields


def _fields_to_slots(user_input: dict) -> dict:
    """Convert flat form fields back to time_slots dict."""
    return {
        slot: {
            "start":  user_input[f"{slot}_start"],
            "volume": float(user_input[f"{slot}_volume"]),
        }
        for slot in SLOT_KEYS
    }


def _time_slots_schema(defaults: dict) -> vol.Schema:
    d = _slots_to_fields(defaults)
    return vol.Schema({
        vol.Optional("morning_start",    default=d["morning_start"]):    _TEXT,
        vol.Optional("morning_volume",   default=d["morning_volume"]):   _SLIDER_0_1,
        vol.Optional("afternoon_start",  default=d["afternoon_start"]):  _TEXT,
        vol.Optional("afternoon_volume", default=d["afternoon_volume"]): _SLIDER_0_1,
        vol.Optional("evening_start",    default=d["evening_start"]):    _TEXT,
        vol.Optional("evening_volume",   default=d["evening_volume"]):   _SLIDER_0_1,
        vol.Optional("night_start",      default=d["night_start"]):      _TEXT,
        vol.Optional("night_volume",     default=d["night_volume"]):     _SLIDER_0_1,
    })


def _greetings_schema(defaults: dict) -> vol.Schema:
    d = _greetings_to_text(defaults)
    return vol.Schema({
        vol.Optional("morning_greetings",   default=d["morning_greetings"]):   _MULTILINE,
        vol.Optional("afternoon_greetings", default=d["afternoon_greetings"]): _MULTILINE,
        vol.Optional("evening_greetings",   default=d["evening_greetings"]):   _MULTILINE,
        vol.Optional("night_greetings",     default=d["night_greetings"]):     _MULTILINE,
    })


# ===========================================================================
# CONFIG FLOW (setup iniziale, guidato, step-by-step)
# ===========================================================================

class UniversalNotifierConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial setup via UI."""

    VERSION = 1

    def __init__(self):
        self._data: dict = {}

    # ── Step 1: Global settings + DND ──────────────────────────────────────

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            dnd_start = user_input.get("dnd_start", "")
            dnd_end   = user_input.get("dnd_end", "")
            if not _is_valid_time(dnd_start):
                errors["dnd_start"] = "invalid_time"
            elif not _is_valid_time(dnd_end):
                errors["dnd_end"] = "invalid_time"
            else:
                self._data.update({
                    "assistant_name":  user_input["assistant_name"],
                    "date_format":     user_input["date_format"],
                    "include_time":    user_input["include_time"],
                    "bold_prefix":     user_input["bold_prefix"],
                    "priority_volume": float(user_input["priority_volume"]),
                    "person_entities": user_input.get("person_entities", []),
                    "dnd": {"start": dnd_start, "end": dnd_end},
                })
                return await self.async_step_time_slots()

        schema = vol.Schema({
            vol.Optional("assistant_name",  default=DEFAULT_ASSISTANT_NAME):  _TEXT,
            vol.Optional("date_format",     default=DEFAULT_DATE_FORMAT):     _TEXT,
            vol.Optional("include_time",    default=DEFAULT_INCLUDE_TIME):    _BOOL,
            vol.Optional("bold_prefix",     default=DEFAULT_BOLD_PREFIX):     _BOOL,
            vol.Optional("priority_volume", default=DEFAULT_PRIORITY_VOLUME): _SLIDER_0_1,
            vol.Optional("person_entities", default=[]):                      _PERSON_MULTI,
            vol.Optional("dnd_start", default=DEFAULT_DND["start"]): _TEXT,
            vol.Optional("dnd_end",   default=DEFAULT_DND["end"]):   _TEXT,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    # ── Step 2: Time slots ─────────────────────────────────────────────────

    async def async_step_time_slots(self, user_input=None):
        errors = {}

        if user_input is not None:
            valid = True
            for slot in SLOT_KEYS:
                t = user_input.get(f"{slot}_start", "")
                if not _is_valid_time(t):
                    errors[f"{slot}_start"] = "invalid_time"
                    valid = False
            if valid:
                self._data["time_slots"] = _fields_to_slots(user_input)
                return await self.async_step_greetings()

        return self.async_show_form(
            step_id="time_slots",
            data_schema=_time_slots_schema(DEFAULT_TIME_SLOTS),
            errors=errors,
        )

    # ── Step 3: Greetings ─────────────────────────────────────────────────

    async def async_step_greetings(self, user_input=None):
        if user_input is not None:
            self._data["greetings"] = _text_to_greetings(user_input)
            return await self.async_step_add_first_channel()

        return self.async_show_form(
            step_id="greetings",
            data_schema=_greetings_schema(DEFAULT_GREETINGS),
        )

    # ── Step 4: First channel (required) → create entry ───────────────────

    async def async_step_add_first_channel(self, user_input=None):
        errors = {}

        if user_input is not None:
            alias   = (user_input.get("alias") or "").strip()
            service = (user_input.get("service") or "").strip()

            if not alias:
                errors["alias"] = "required"
            elif not service or "." not in service:
                errors["service"] = "invalid_service"
            else:
                alt_raw = (user_input.get("alt_services") or "{}").strip()
                try:
                    alt_services = json.loads(alt_raw) if alt_raw else {}
                    if not isinstance(alt_services, dict):
                        raise ValueError
                except (json.JSONDecodeError, ValueError):
                    errors["alt_services"] = "invalid_json"
                    alt_services = None

                if alt_services is not None:
                    self._data["channels"] = {
                        alias: {
                            "service":      service,
                            "target":       (user_input.get("target") or "").strip(),
                            "is_voice":     user_input.get("is_voice", False),
                            "alt_services": alt_services,
                        }
                    }
                    await self.async_set_unique_id(DOMAIN)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(title="Universal Notifier", data=self._data)

        schema = vol.Schema({
            vol.Required("alias"):                       _TEXT,
            vol.Required("service"):                     _TEXT,
            vol.Optional("target",       default=""):    _TEXT,
            vol.Optional("is_voice",     default=False): _BOOL,
            vol.Optional("alt_services", default="{}"):  _MULTILINE,
        })
        return self.async_show_form(step_id="add_first_channel", data_schema=schema, errors=errors)

    # ── Attach OptionsFlow ─────────────────────────────────────────────────

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return UniversalNotifierOptionsFlow(config_entry)


# ===========================================================================
# OPTIONS FLOW (menu-driven per editing post-setup)
# ===========================================================================

class UniversalNotifierOptionsFlow(config_entries.OptionsFlow):
    """Handle reconfiguration via UI (Settings → Integrations → Configure)."""

    def __init__(self, config_entry):
        self._entry = config_entry
        # Accumula tutte le options correnti (non perdiamo sezioni non modificate)
        self._current_options: dict = dict(config_entry.options)
        # Valori effettivi = data + options (options sovrascrivono)
        self._effective: dict = {**config_entry.data, **self._current_options}

    def _save(self):
        """Return async_create_entry with the full current options dict."""
        return self.async_create_entry(data=self._current_options)

    # ── Menu principale ────────────────────────────────────────────────────

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(
            step_id="init",
            menu_options=["global_settings", "dnd", "time_slots", "greetings", "channels_menu"],
        )

    # ── Global settings ────────────────────────────────────────────────────

    async def async_step_global_settings(self, user_input=None):
        if user_input is not None:
            self._current_options.update({
                "assistant_name":  user_input["assistant_name"],
                "date_format":     user_input["date_format"],
                "include_time":    user_input["include_time"],
                "bold_prefix":     user_input["bold_prefix"],
                "priority_volume": float(user_input["priority_volume"]),
                "person_entities": user_input.get("person_entities", []),
            })
            return self._save()

        eff = self._effective
        schema = vol.Schema({
            vol.Optional("assistant_name",  default=eff.get("assistant_name",  DEFAULT_ASSISTANT_NAME)):  _TEXT,
            vol.Optional("date_format",     default=eff.get("date_format",     DEFAULT_DATE_FORMAT)):     _TEXT,
            vol.Optional("include_time",    default=eff.get("include_time",    DEFAULT_INCLUDE_TIME)):    _BOOL,
            vol.Optional("bold_prefix",     default=eff.get("bold_prefix",     DEFAULT_BOLD_PREFIX)):     _BOOL,
            vol.Optional("priority_volume", default=eff.get("priority_volume", DEFAULT_PRIORITY_VOLUME)): _SLIDER_0_1,
            vol.Optional("person_entities", default=eff.get("person_entities", [])): _PERSON_MULTI,
        })
        return self.async_show_form(step_id="global_settings", data_schema=schema)

    # ── DND ────────────────────────────────────────────────────────────────

    async def async_step_dnd(self, user_input=None):
        errors = {}

        if user_input is not None:
            dnd_start = user_input.get("dnd_start", "")
            dnd_end   = user_input.get("dnd_end", "")
            if not _is_valid_time(dnd_start):
                errors["dnd_start"] = "invalid_time"
            elif not _is_valid_time(dnd_end):
                errors["dnd_end"] = "invalid_time"
            else:
                self._current_options["dnd"] = {"start": dnd_start, "end": dnd_end}
                return self._save()

        dnd = self._effective.get("dnd", DEFAULT_DND)
        schema = vol.Schema({
            vol.Optional("dnd_start", default=dnd.get("start", DEFAULT_DND["start"])): _TEXT,
            vol.Optional("dnd_end",   default=dnd.get("end",   DEFAULT_DND["end"])):   _TEXT,
        })
        return self.async_show_form(step_id="dnd", data_schema=schema, errors=errors)

    # ── Time slots ─────────────────────────────────────────────────────────

    async def async_step_time_slots(self, user_input=None):
        errors = {}

        if user_input is not None:
            valid = True
            for slot in SLOT_KEYS:
                t = user_input.get(f"{slot}_start", "")
                if not _is_valid_time(t):
                    errors[f"{slot}_start"] = "invalid_time"
                    valid = False
            if valid:
                self._current_options["time_slots"] = _fields_to_slots(user_input)
                return self._save()

        return self.async_show_form(
            step_id="time_slots",
            data_schema=_time_slots_schema(self._effective.get("time_slots", DEFAULT_TIME_SLOTS)),
            errors=errors,
        )

    # ── Greetings ──────────────────────────────────────────────────────────

    async def async_step_greetings(self, user_input=None):
        if user_input is not None:
            self._current_options["greetings"] = _text_to_greetings(user_input)
            return self._save()

        return self.async_show_form(
            step_id="greetings",
            data_schema=_greetings_schema(self._effective.get("greetings", DEFAULT_GREETINGS)),
        )

    # ── Channels menu ──────────────────────────────────────────────────────

    async def async_step_channels_menu(self, user_input=None):
        return self.async_show_menu(
            step_id="channels_menu",
            menu_options=["add_channel", "remove_channel"],
        )

    # ── Add channel ────────────────────────────────────────────────────────

    async def async_step_add_channel(self, user_input=None):
        errors = {}

        if user_input is not None:
            alias   = (user_input.get("alias") or "").strip()
            service = (user_input.get("service") or "").strip()

            if not alias:
                errors["alias"] = "required"
            elif not service:
                errors["service"] = "required"
            elif "." not in service:
                errors["service"] = "invalid_service"
            else:
                alt_raw = (user_input.get("alt_services") or "{}").strip()
                try:
                    alt_services = json.loads(alt_raw) if alt_raw else {}
                    if not isinstance(alt_services, dict):
                        raise ValueError
                except (json.JSONDecodeError, ValueError):
                    errors["alt_services"] = "invalid_json"
                    alt_services = None

                if alt_services is not None:
                    channels = dict(self._current_options.get(
                        "channels",
                        self._effective.get("channels", {}),
                    ))
                    channels[alias] = {
                        "service":      service,
                        "target":       (user_input.get("target") or "").strip(),
                        "is_voice":     user_input.get("is_voice", False),
                        "alt_services": alt_services,
                    }
                    self._current_options["channels"] = channels
                    return self._save()

        schema = vol.Schema({
            vol.Required("alias"):                       _TEXT,
            vol.Required("service"):                     _TEXT,
            vol.Optional("target",       default=""):    _TEXT,
            vol.Optional("is_voice",     default=False): _BOOL,
            vol.Optional("alt_services", default="{}"):  _MULTILINE,
        })
        return self.async_show_form(step_id="add_channel", data_schema=schema, errors=errors)

    # ── Remove channel ─────────────────────────────────────────────────────

    async def async_step_remove_channel(self, user_input=None):
        channels = self._effective.get("channels", {})

        if not channels:
            # Nessun canale da rimuovere — torna al menu
            return await self.async_step_channels_menu()

        if user_input is not None:
            alias_to_remove = user_input.get("alias")
            channels = dict(self._current_options.get("channels", dict(channels)))
            channels.pop(alias_to_remove, None)
            self._current_options["channels"] = channels
            return self._save()

        schema = vol.Schema({
            vol.Required("alias"): SelectSelector(
                SelectSelectorConfig(
                    options=list(channels.keys()),
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        })
        return self.async_show_form(step_id="remove_channel", data_schema=schema)
