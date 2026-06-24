"""Tests for sensor.py — volume, family, default_player sensors."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from custom_components.universal_notifier.const import DOMAIN
from custom_components.universal_notifier.sensor import (
    UNotifierDefaultPlayerSensor, UNotifierFamilySensor, UNotifierVolumeSensor)
from tests.conftest import DEFAULT_DATA


def _make_conf():
    """Return a copy of DEFAULT_DATA suitable for sensor constructors."""
    return DEFAULT_DATA.copy()


def _make_entry():
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


class TestVolumeSensor:
    @freeze_time("2026-06-17 09:00:00")  # Wednesday morning
    def test_volume_sensor_state(self):
        """Volume sensor should report current slot volume as percentage."""
        sensor = UNotifierVolumeSensor(_make_conf(), _make_entry())
        # Morning volume is 0.35 → 35
        assert sensor.native_value == 35

    def test_volume_sensor_attributes(self):
        """Volume sensor should have slot and volume attributes."""
        sensor = UNotifierVolumeSensor(_make_conf(), _make_entry())
        attrs = sensor.extra_state_attributes
        assert "current_slot" in attrs
        assert "raw_volume" in attrs


class TestFamilySensor:
    @freeze_time("2026-06-17 10:00:00")
    def test_family_sensor_no_persons(self):
        """With no person entities configured, family sensor should be 'not_home'."""
        mock_hass = MagicMock()
        mock_hass.states = MagicMock()
        mock_hass.states.get = MagicMock(return_value=None)

        sensor = UNotifierFamilySensor(mock_hass, _make_conf(), _make_entry())
        assert sensor.native_value == "not_home"

    @freeze_time("2026-06-17 10:00:00")
    def test_family_sensor_person_home(self):
        """When a person is home, sensor should be 'home'."""
        mock_hass = MagicMock()
        person_state = MagicMock()
        person_state.state = "home"
        mock_hass.states = MagicMock()
        mock_hass.states.get = MagicMock(return_value=person_state)

        conf = _make_conf()
        conf["person_entities"] = ["person.test_user"]
        sensor = UNotifierFamilySensor(mock_hass, conf, _make_entry())
        assert sensor.native_value == "home"


class TestDefaultPlayerSensor:
    def test_default_player_sensor_state(self):
        """Default player sensor should list configured players."""
        sensor = UNotifierDefaultPlayerSensor(_make_conf(), _make_entry())
        # Only test_voice channel has a default_media_player configured
        assert sensor.native_value is not None

    def test_default_player_attributes(self):
        """Default player sensor should have voice_defaults attribute."""
        sensor = UNotifierDefaultPlayerSensor(_make_conf(), _make_entry())
        attrs = sensor.extra_state_attributes
        assert isinstance(attrs, dict)
