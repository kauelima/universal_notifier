"""Unit tests for utils.py — pure functions, no HA dependencies."""
from __future__ import annotations

from datetime import time

import pytest

from custom_components.universal_notifier.utils import (apply_formatting,
                                                        clean_text_for_tts,
                                                        escape_markdownv2,
                                                        estimate_tts_duration,
                                                        get_current_slot_info,
                                                        is_time_in_range,
                                                        normalize_parse_mode,
                                                        sanitize_text_visual)

# ============================================================================
# estimate_tts_duration
# ============================================================================

class TestEstimateTTSDuration:
    def test_empty_text_returns_zero(self):
        assert estimate_tts_duration("", buffer=2.5) == 0

    def test_none_text_returns_zero(self):
        assert estimate_tts_duration(None, buffer=2.5) == 0  # type: ignore[arg-type]

    def test_short_text(self):
        # "Hello world" = 2 words → 2/1.5 + 2.5 = 3.83, but min is 2.5+2.0=4.5
        result = estimate_tts_duration("Hello world", buffer=2.5)
        assert result == pytest.approx(4.5, abs=0.1)

    def test_long_text(self):
        text = " ".join(["word"] * 60)  # 60 words
        result = estimate_tts_duration(text, buffer=2.5)
        # 60/1.5 + 2.5 = 42.5
        assert result == pytest.approx(42.5, abs=0.1)

    def test_custom_buffer(self):
        result = estimate_tts_duration("Hello", buffer=5.0)
        # 1 word / 1.5 + 5.0 = 5.67, min is 5.0+2.0=7.0
        assert result == pytest.approx(7.0, abs=0.1)


# ============================================================================
# is_time_in_range
# ============================================================================

class TestIsTimeInRange:
    def test_normal_range_inside(self):
        assert is_time_in_range("10:00", "18:00", time(14, 0)) is True

    def test_normal_range_outside(self):
        assert is_time_in_range("10:00", "18:00", time(20, 0)) is False

    def test_normal_range_at_start(self):
        assert is_time_in_range("10:00", "18:00", time(10, 0)) is True

    def test_normal_range_at_end(self):
        assert is_time_in_range("10:00", "18:00", time(18, 0)) is True

    def test_overnight_range_inside(self):
        # 23:00 - 06:00 wraps midnight
        assert is_time_in_range("23:00", "06:00", time(2, 0)) is True

    def test_overnight_range_outside(self):
        assert is_time_in_range("23:00", "06:00", time(12, 0)) is False

    def test_overnight_range_at_start(self):
        assert is_time_in_range("23:00", "06:00", time(23, 0)) is True

    def test_overnight_range_at_end(self):
        assert is_time_in_range("23:00", "06:00", time(6, 0)) is True

    def test_overnight_range_late_night(self):
        assert is_time_in_range("23:00", "06:00", time(23, 30)) is True


# ============================================================================
# get_current_slot_info
# ============================================================================

class TestGetCurrentSlotInfo:
    SLOTS_WEEKDAY_WEEKEND = {
        "weekday": {
            "morning":   {"start": "07:00", "volume": 0.35},
            "afternoon": {"start": "12:00", "volume": 0.40},
            "evening":   {"start": "19:00", "volume": 0.30},
            "night":     {"start": "21:30", "volume": 0.10},
        },
        "weekend": {
            "morning":   {"start": "08:00", "volume": 0.30},
            "afternoon": {"start": "14:00", "volume": 0.40},
            "evening":   {"start": "19:00", "volume": 0.30},
            "night":     {"start": "22:30", "volume": 0.10},
        },
    }

    def test_weekday_morning(self):
        slot, vol = get_current_slot_info(
            self.SLOTS_WEEKDAY_WEEKEND, time(9, 0), 0, [5, 6]  # Monday
        )
        assert slot == "morning"
        assert vol == 0.35

    def test_weekday_afternoon(self):
        slot, vol = get_current_slot_info(
            self.SLOTS_WEEKDAY_WEEKEND, time(15, 0), 2, [5, 6]  # Wednesday
        )
        assert slot == "afternoon"
        assert vol == 0.40

    def test_weekend_morning_uses_weekend_config(self):
        slot, vol = get_current_slot_info(
            self.SLOTS_WEEKDAY_WEEKEND, time(9, 0), 5, [5, 6]  # Saturday
        )
        assert slot == "morning"
        assert vol == 0.30  # weekend volume, not weekday 0.35

    def test_weekend_afternoon(self):
        slot, vol = get_current_slot_info(
            self.SLOTS_WEEKDAY_WEEKEND, time(15, 0), 6, [5, 6]  # Sunday
        )
        assert slot == "afternoon"
        assert vol == 0.40

    def test_empty_config_uses_defaults(self):
        slot, vol = get_current_slot_info({}, time(10, 0), 0, [5, 6])
        assert slot in ("morning", "afternoon", "evening", "night")
        assert 0.0 <= vol <= 1.0

    def test_old_flat_format(self):
        """Old flat format (no weekday/weekend nesting) should still work."""
        flat = {
            "morning":   {"start": "07:00", "volume": 0.50},
            "afternoon": {"start": "12:00", "volume": 0.60},
            "evening":   {"start": "19:00", "volume": 0.40},
            "night":     {"start": "22:00", "volume": 0.20},
        }
        slot, vol = get_current_slot_info(flat, time(10, 0), 0, [5, 6])
        assert slot == "morning"
        assert vol == 0.50

    def test_night_slot_wraps(self):
        """Night slot (21:30) should apply from 21:30 until 07:00 next day."""
        slot, vol = get_current_slot_info(
            self.SLOTS_WEEKDAY_WEEKEND, time(23, 0), 0, [5, 6]
        )
        assert slot == "night"
        assert vol == 0.10

    def test_early_morning_before_first_slot(self):
        """Before 07:00 should still be 'night' (last slot wraps)."""
        slot, vol = get_current_slot_info(
            self.SLOTS_WEEKDAY_WEEKEND, time(5, 0), 0, [5, 6]
        )
        assert slot == "night"
        assert vol == 0.10

    def test_custom_weekend_days(self):
        """Custom weekend_days (e.g., Friday=4) should use weekend config."""
        slot, vol = get_current_slot_info(
            self.SLOTS_WEEKDAY_WEEKEND, time(9, 0), 4, [4, 5]  # Friday
        )
        assert slot == "morning"
        assert vol == 0.30  # weekend volume


# ============================================================================
# clean_text_for_tts
# ============================================================================

class TestCleanTextForTTS:
    def test_strips_html_tags(self):
        assert clean_text_for_tts("<b>Hello</b> <i>world</i>") == "Hello world"

    def test_strips_links(self):
        assert clean_text_for_tts('<a href="http://example.com">link</a>') == "link"

    def test_strips_markdown(self):
        assert clean_text_for_tts("**bold** and *italic*") == "bold and italic"

    def test_strips_urls(self):
        assert clean_text_for_tts("Visit http://example.com now") == "Visit now"

    def test_strips_emoji(self):
        assert clean_text_for_tts("Hello 🏠🌡️ world") == "Hello world"

    def test_preserves_accented_chars(self):
        text = "Perché è così àèìòù"
        result = clean_text_for_tts(text)
        assert "Perché" in result
        assert "àèìòù" in result

    def test_empty_text(self):
        assert clean_text_for_tts("") == ""

    def test_none_text(self):
        assert clean_text_for_tts(None) == ""  # type: ignore[arg-type]

    def test_collapses_whitespace(self):
        assert clean_text_for_tts("hello   world") == "hello world"


# ============================================================================
# sanitize_text_visual
# ============================================================================

class TestSanitizeTextVisual:
    def test_html_mode_removes_markdown(self):
        result = sanitize_text_visual("**bold** text", "html")
        assert result == "bold text"

    def test_html_mode_preserves_html(self):
        result = sanitize_text_visual("<b>bold</b> text", "html")
        assert "<b>bold</b>" in result

    def test_markdown_mode_removes_html(self):
        result = sanitize_text_visual("<b>bold</b> text", "markdown")
        assert "<b>" not in result
        assert "bold" in result

    def test_plain_text_removes_markdown(self):
        result = sanitize_text_visual("**bold** and *italic*", "plain_text")
        assert "**" not in result
        assert "*" not in result.replace("italic", "")

    def test_empty_text(self):
        assert sanitize_text_visual("", "html") == ""

    def test_none_text(self):
        assert sanitize_text_visual(None, "html") == ""  # type: ignore[arg-type]

    def test_none_parse_mode(self):
        result = sanitize_text_visual("**bold**", None)
        assert "**" not in result


# ============================================================================
# apply_formatting
# ============================================================================

class TestApplyFormatting:
    def test_bold_html(self):
        assert apply_formatting("text", "html", "bold") == "<b>text</b>"

    def test_bold_markdownv2(self):
        assert apply_formatting("text", "markdownv2", "bold") == "*text*"

    def test_bold_markdown(self):
        assert apply_formatting("text", "markdown", "bold") == "**text**"

    def test_bold_plain_text(self):
        assert apply_formatting("text", "plain_text", "bold") == "text"

    def test_empty_text(self):
        assert apply_formatting("", "html", "bold") == ""

    def test_none_text(self):
        assert apply_formatting(None, "html", "bold") == ""  # type: ignore[arg-type]


# ============================================================================
# escape_markdownv2
# ============================================================================

class TestEscapeMarkdownV2:
    def test_escapes_special_chars(self):
        result = escape_markdownv2("Hello! How are you?")
        assert "\\!" in result
        # ? is NOT a MarkdownV2 special char — should not be escaped
        assert "?" in result and "\\?" not in result

    def test_preserves_bold(self):
        result = escape_markdownv2("**bold text**")
        assert "*bold text*" in result

    def test_preserves_italic(self):
        result = escape_markdownv2("*italic*")
        assert "*italic*" in result

    def test_empty_text(self):
        assert escape_markdownv2("") == ""

    def test_none_text(self):
        assert escape_markdownv2(None) == ""  # type: ignore[arg-type]

    def test_escapes_parentheses(self):
        result = escape_markdownv2("test (value)")
        assert "\\(" in result
        assert "\\)" in result

    def test_escapes_dot(self):
        result = escape_markdownv2("v1.0")
        assert "\\." in result


# ============================================================================
# normalize_parse_mode
# ============================================================================

class TestNormalizeParseMode:
    def test_telegram_html(self):
        assert normalize_parse_mode("html", "telegram_bot") == "html"

    def test_telegram_markdown(self):
        assert normalize_parse_mode("markdown", "telegram_bot") == "markdown"

    def test_telegram_markdownv2(self):
        assert normalize_parse_mode("markdownv2", "telegram_bot") == "markdownv2"

    def test_telegram_plain_text(self):
        assert normalize_parse_mode("plain_text", "telegram_bot") == "plain_text"

    def test_telegram_invalid_falls_back_to_html(self):
        assert normalize_parse_mode("rich_text", "telegram_bot") == "html"

    def test_telegram_case_insensitive(self):
        assert normalize_parse_mode("HTML", "telegram_bot") == "html"

    def test_non_telegram_passes_through(self):
        assert normalize_parse_mode("HTML", "notify") == "html"

    def test_none_returns_none(self):
        assert normalize_parse_mode(None, "telegram_bot") is None

    def test_empty_returns_none(self):
        assert normalize_parse_mode("", "telegram_bot") is None
