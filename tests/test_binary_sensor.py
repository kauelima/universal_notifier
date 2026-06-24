"""Tests for binary_sensor.py — DND binary sensor."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from custom_components.universal_notifier.binary_sensor import \
    UNotifierDNDSensor
from custom_components.universal_notifier.const import DOMAIN
from tests.conftest import DEFAULT_DATA


def _make_conf():
    return DEFAULT_DATA.copy()


def _make_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def _make_sensor(conf=None):
    """Create a DND sensor with mocked hass and entity registry."""
    mock_hass = MagicMock()
    mock_hass.states = MagicMock()
    mock_hass.states.get = MagicMock(return_value=None)

    # Patch er.async_get so the sensor's _check_override works
    mock_ent_reg = MagicMock()
    mock_ent_reg.async_get_entity_id = MagicMock(return_value=None)

    with patch(
        "custom_components.universal_notifier.binary_sensor.er.async_get",
        return_value=mock_ent_reg,
    ):
        sensor = UNotifierDNDSensor(conf or _make_conf(), _make_entry())
        sensor.hass = mock_hass

    sensor._hass = mock_hass
    sensor._ent_reg = mock_ent_reg
    return sensor


class TestDNDBinarySensor:
    @freeze_time("2026-06-17 10:00:00")  # Wednesday, outside DND
    def test_dnd_sensor_off_outside_dnd(self):
        """DND sensor should be off outside DND hours."""
        sensor = _make_sensor()
        assert sensor.is_on is False

    @freeze_time("2026-06-17 02:00:00")  # Wednesday, inside DND (23:00-06:00)
    def test_dnd_sensor_on_during_dnd(self):
        """DND sensor should be on during DND hours."""
        sensor = _make_sensor()
        assert sensor.is_on is True

    @freeze_time("2026-06-17 10:00:00")
    def test_dnd_sensor_on_with_override(self):
        """DND sensor should be on when override switch is on."""
        mock_hass = MagicMock()
        override_state = MagicMock()
        override_state.state = "on"
        mock_hass.states = MagicMock()
        mock_hass.states.get = MagicMock(return_value=override_state)

        mock_ent_reg = MagicMock()
        mock_ent_reg.async_get_entity_id = MagicMock(
            return_value="switch.universal_notifier_dnd_override"
        )

        with patch(
            "custom_components.universal_notifier.binary_sensor.er.async_get",
            return_value=mock_ent_reg,
        ):
            sensor = UNotifierDNDSensor(_make_conf(), _make_entry())
            sensor.hass = mock_hass

        assert sensor.is_on is True
