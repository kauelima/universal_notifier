"""Tests for number.py — TTS buffer slider."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.universal_notifier.const import DOMAIN
from custom_components.universal_notifier.number import UNotifierBufferVoice


def _make_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def _make_hass():
    hass = MagicMock()
    hass.data = {DOMAIN: {"test_entry_id": {"tts_buffer": 2.5}}}
    return hass


class TestTTSBufferNumber:
    def test_tts_buffer_default(self):
        """TTS buffer should default to 2.5."""
        num = UNotifierBufferVoice(_make_hass(), _make_entry())
        assert num.native_value == 2.5

    def test_tts_buffer_range(self):
        """TTS buffer should have correct min/max range."""
        num = UNotifierBufferVoice(_make_hass(), _make_entry())
        assert num.native_min_value == 0.5
        assert num.native_max_value == 10.0
        assert num.native_step == 0.5

    async def test_tts_buffer_change(self):
        """Changing TTS buffer should update hass.data."""
        hass = _make_hass()
        num = UNotifierBufferVoice(hass, _make_entry())
        num.async_write_ha_state = MagicMock()

        await num.async_set_native_value(5.0)
        assert num.native_value == 5.0
        assert hass.data[DOMAIN]["test_entry_id"]["tts_buffer"] == 5.0
