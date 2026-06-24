"""Tests for select.py — PriorityVolumeSelect, TextFormatSelect, NotificationModeSelect."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.universal_notifier.const import (CONF_PRIORITY_VOLUME,
                                                        DOMAIN)
from custom_components.universal_notifier.select import (
    NotificationModeSelect, PriorityVolumeSelect, TextFormatSelect)
from tests.conftest import DEFAULT_DATA


def _make_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = DEFAULT_DATA.copy()
    entry.options = {}
    return entry


def _make_hass():
    """Create a minimal mock hass with data store for runtime values."""
    hass = MagicMock()
    hass.data = {DOMAIN: {"test_entry_id": {"conf": DEFAULT_DATA.copy()}}}
    return hass


class TestPriorityVolumeSelect:
    def test_priority_volume_options(self):
        """Priority volume select should have volume options from 0.1 to 1.0."""
        sel = PriorityVolumeSelect(_make_hass(), _make_entry())
        options = sel.options
        assert "0.1" in options
        assert "0.5" in options
        assert "1.0" in options

    def test_priority_volume_default_value(self):
        """Priority volume should default to configured value."""
        sel = PriorityVolumeSelect(_make_hass(), _make_entry())
        # DEFAULT_DATA has CONF_PRIORITY_VOLUME: 0.9
        assert sel.current_option == "0.9"

    async def test_priority_volume_change(self):
        """Changing priority volume should update hass.data runtime value."""
        hass = _make_hass()
        sel = PriorityVolumeSelect(hass, _make_entry())
        sel.async_write_ha_state = MagicMock()

        await sel.async_select_option("0.5")
        assert hass.data[DOMAIN]["test_entry_id"]["runtime_priority_vol"] == 0.5


class TestTextFormatSelect:
    def test_text_format_options(self):
        """Text format select should have format options."""
        sel = TextFormatSelect(_make_hass(), _make_entry())
        options = sel.options
        assert "html" in options
        assert "markdown" in options
        assert "markdownv2" in options
        assert "plain_text" in options

    def test_text_format_default(self):
        """Text format should default to html."""
        sel = TextFormatSelect(_make_hass(), _make_entry())
        assert sel.current_option == "html"

    async def test_text_format_change(self):
        """Changing text format should update hass.data."""
        hass = _make_hass()
        sel = TextFormatSelect(hass, _make_entry())
        sel.async_write_ha_state = MagicMock()

        await sel.async_select_option("markdown")
        assert hass.data[DOMAIN]["test_entry_id"]["text_format"] == "markdown"


class TestNotificationModeSelect:
    def test_notification_mode_options(self):
        """Notification mode select should have mode options."""
        sel = NotificationModeSelect(_make_hass(), _make_entry())
        options = sel.options
        assert "Normal" in options
        assert "Voice home" in options
        assert "Text home" in options

    def test_notification_mode_default(self):
        """Notification mode should default to Normal."""
        sel = NotificationModeSelect(_make_hass(), _make_entry())
        assert sel.current_option == "Normal"

    async def test_notification_mode_change(self):
        """Changing notification mode should update hass.data."""
        hass = _make_hass()
        sel = NotificationModeSelect(hass, _make_entry())
        sel.async_write_ha_state = MagicMock()

        await sel.async_select_option("Voice home")
        assert hass.data[DOMAIN]["test_entry_id"]["notification_mode"] == "Voice home"
