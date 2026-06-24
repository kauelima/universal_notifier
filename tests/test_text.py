"""Tests for text.py — last message text entity."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.universal_notifier.const import DOMAIN
from custom_components.universal_notifier.text import UNotifierLastMessageText


def _make_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


class TestLastMessageText:
    def test_last_message_default_empty(self):
        """Last message text entity should default to empty string."""
        entity = UNotifierLastMessageText(_make_entry())
        assert entity.native_value == ""

    async def test_last_message_set_value(self):
        """Setting value should update native_value."""
        entity = UNotifierLastMessageText(_make_entry())
        entity.async_write_ha_state = MagicMock()
        await entity.async_set_value("Test message")
        assert entity.native_value == "Test message"

    async def test_last_message_truncation(self):
        """Long messages should be truncated to 255 chars."""
        entity = UNotifierLastMessageText(_make_entry())
        entity.async_write_ha_state = MagicMock()
        long_msg = "x" * 300
        await entity.async_set_value(long_msg)
        assert len(entity.native_value) <= 255
