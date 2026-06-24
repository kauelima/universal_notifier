"""Tests for switch.py — DND override toggle."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.universal_notifier.const import DOMAIN
from custom_components.universal_notifier.switch import \
    UNotifierDNDOverrideSwitch


def _make_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


class TestDNDOverrideSwitch:
    def test_dnd_override_default_off(self):
        """DND override switch should default to off."""
        switch = UNotifierDNDOverrideSwitch(_make_entry())
        assert switch.is_on is False

    async def test_dnd_override_turn_on(self):
        """Turning on DND override should set is_on to True."""
        switch = UNotifierDNDOverrideSwitch(_make_entry())
        switch.async_write_ha_state = MagicMock()
        await switch.async_turn_on()
        assert switch.is_on is True

    async def test_dnd_override_turn_off(self):
        """Turning off DND override should set is_on to False."""
        switch = UNotifierDNDOverrideSwitch(_make_entry())
        switch.async_write_ha_state = MagicMock()
        await switch.async_turn_on()
        assert switch.is_on is True
        await switch.async_turn_off()
        assert switch.is_on is False
