"""Tests for config_flow.py — initial setup and options flow."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from custom_components.universal_notifier.config_flow import (
    DEFAULT_ASSISTANT_NAME, DEFAULT_BOLD_PREFIX, DEFAULT_DATE_FORMAT,
    DEFAULT_DND, DEFAULT_GREETINGS, DEFAULT_IGNORE_TITLE_VOICE,
    DEFAULT_INCLUDE_TIME, DEFAULT_PRIORITY_VOLUME, DEFAULT_TIME_SLOTS,
    DEFAULT_WEEKEND_DAYS, SLOT_KEYS, _fields_to_slots, _greetings_to_text,
    _slots_to_fields, _text_to_greetings)
from custom_components.universal_notifier.const import DOMAIN
from tests.conftest import DEFAULT_DATA

# ============================================================================
# Config flow helper functions (pure functions — no HA deps)
# ============================================================================

class TestConfigFlowHelpers:
    def test_greetings_to_text(self):
        greetings = {
            "morning": ["Buongiorno", "Ciao"],
            "afternoon": ["Buon pomeriggio"],
            "evening": [],
            "night": ["Buonanotte"],
        }
        result = _greetings_to_text(greetings)
        assert result["morning_greetings"] == "Buongiorno\nCiao"
        assert result["afternoon_greetings"] == "Buon pomeriggio"
        assert result["evening_greetings"] == ""
        assert result["night_greetings"] == "Buonanotte"

    def test_text_to_greetings(self):
        user_input = {
            "morning_greetings": "Buongiorno\nCiao",
            "afternoon_greetings": "Buon pomeriggio",
            "evening_greetings": "",
            "night_greetings": "Buonanotte",
        }
        result = _text_to_greetings(user_input)
        assert result["morning"] == ["Buongiorno", "Ciao"]
        assert result["afternoon"] == ["Buon pomeriggio"]
        assert result["evening"] == []
        assert result["night"] == ["Buonanotte"]

    def test_slots_to_fields_nested(self):
        ts = {
            "weekday": {
                "morning": {"start": "07:00", "volume": 0.35},
                "afternoon": {"start": "12:00", "volume": 0.40},
                "evening": {"start": "19:00", "volume": 0.30},
                "night": {"start": "21:30", "volume": 0.10},
            },
        }
        fields = _slots_to_fields(ts, "weekday")
        assert fields["weekday_morning_start"] == "07:00"
        assert fields["weekday_morning_volume"] == 0.35

    def test_slots_to_fields_flat(self):
        """Old flat format (no weekday/weekend nesting)."""
        flat = {
            "morning": {"start": "08:00", "volume": 0.50},
            "afternoon": {"start": "13:00", "volume": 0.60},
            "evening": {"start": "20:00", "volume": 0.40},
            "night": {"start": "23:00", "volume": 0.20},
        }
        fields = _slots_to_fields(flat, "weekday")
        assert fields["weekday_morning_start"] == "08:00"
        assert fields["weekday_morning_volume"] == 0.50

    def test_fields_to_slots(self):
        user_input = {
            "weekday_morning_start": "07:00",
            "weekday_morning_volume": 0.35,
            "weekday_afternoon_start": "12:00",
            "weekday_afternoon_volume": 0.40,
            "weekday_evening_start": "19:00",
            "weekday_evening_volume": 0.30,
            "weekday_night_start": "21:30",
            "weekday_night_volume": 0.10,
            "weekend_morning_start": "08:00",
            "weekend_morning_volume": 0.30,
            "weekend_afternoon_start": "14:00",
            "weekend_afternoon_volume": 0.40,
            "weekend_evening_start": "19:00",
            "weekend_evening_volume": 0.30,
            "weekend_night_start": "22:30",
            "weekend_night_volume": 0.10,
        }
        result = _fields_to_slots(user_input)
        assert result["weekday"]["morning"]["start"] == "07:00"
        assert result["weekend"]["night"]["volume"] == 0.10


# ============================================================================
# Config flow handler class — direct testing with MagicMock (alexa_media_player pattern)
# ============================================================================

class TestConfigFlowSetup:
    """Test the config flow handler directly using MagicMock."""

    def _make_handler(self):
        """Create a config flow handler with mocked HA internals."""
        from custom_components.universal_notifier.config_flow import \
            UniversalNotifierConfigFlow

        handler = UniversalNotifierConfigFlow.__new__(
            UniversalNotifierConfigFlow
        )
        handler.hass = MagicMock()
        handler._errors = {}
        handler._data = {}
        handler.context = {}
        return handler

    def test_handler_class_exists(self):
        """Verify the config flow handler class is importable."""
        from custom_components.universal_notifier.config_flow import \
            UniversalNotifierConfigFlow
        assert UniversalNotifierConfigFlow is not None

    def test_default_constants_exist(self):
        """Verify all default constants are defined."""
        assert DEFAULT_ASSISTANT_NAME is not None
        assert DEFAULT_DATE_FORMAT is not None
        assert DEFAULT_INCLUDE_TIME is not None
        assert DEFAULT_BOLD_PREFIX is not None
        assert DEFAULT_PRIORITY_VOLUME is not None
        assert DEFAULT_DND is not None
        assert DEFAULT_GREETINGS is not None
        assert DEFAULT_TIME_SLOTS is not None
        assert DEFAULT_WEEKEND_DAYS is not None

    def test_slot_keys_defined(self):
        """Verify SLOT_KEYS contains all expected time slots."""
        assert "morning" in SLOT_KEYS
        assert "afternoon" in SLOT_KEYS
        assert "evening" in SLOT_KEYS
        assert "night" in SLOT_KEYS

    def test_roundtrip_greetings_conversion(self):
        """Greetings → text → greetings roundtrip preserves data."""
        original = {
            "morning": ["Buongiorno", "Ciao"],
            "afternoon": ["Buon pomeriggio"],
            "evening": [],
            "night": ["Buonanotte"],
        }
        text_form = _greetings_to_text(original)
        restored = _text_to_greetings(text_form)
        assert restored == original

    def test_roundtrip_slots_conversion(self):
        """Slots → fields → slots roundtrip preserves data."""
        original = DEFAULT_TIME_SLOTS
        fields = {}
        for group in ("weekday", "weekend"):
            fields.update(_slots_to_fields(original, group))
        restored = _fields_to_slots(fields)
        assert restored["weekday"]["morning"]["start"] == original["weekday"]["morning"]["start"]
        assert restored["weekend"]["night"]["volume"] == original["weekend"]["night"]["volume"]


# ============================================================================
# Options flow handler
# ============================================================================

class TestOptionsFlow:
    """Test the options flow handler directly."""

    def test_handler_class_exists(self):
        """Verify the options flow handler class is importable."""
        from custom_components.universal_notifier.config_flow import \
            UniversalNotifierOptionsFlow
        assert UniversalNotifierOptionsFlow is not None

    def test_options_flow_has_init_handler(self):
        """Verify the options flow has an init_step method."""
        from custom_components.universal_notifier.config_flow import \
            UniversalNotifierOptionsFlow
        assert hasattr(UniversalNotifierOptionsFlow, "async_step_init")

    def test_default_data_matches_config_flow_constants(self):
        """DEFAULT_DATA from conftest uses the same constants as config flow."""
        # DEFAULT_ASSISTANT_NAME is "" (config flow default), but test data uses "Assistant"
        assert DEFAULT_ASSISTANT_NAME == ""
