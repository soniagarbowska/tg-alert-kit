# -*- coding: utf-8 -*-
"""Testy escapowania MarkdownV2."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tg_alert_kit.escape import md, bold, code, italic, mono_block, link


class TestMd:
    def test_plain_text_unchanged(self):
        assert md("hello world") == "hello world"

    def test_escapes_dot(self):
        assert md("v1.4.2") == r"v1\.4\.2"

    def test_escapes_dash(self):
        assert md("eu-west-1") == r"eu\-west\-1"

    def test_escapes_parens(self):
        assert md("(test)") == r"\(test\)"

    def test_escapes_brackets(self):
        assert md("[a]") == r"\[a\]"

    def test_escapes_asterisk(self):
        assert md("2*3") == r"2\*3"

    def test_escapes_all_special(self):
        special = r"\_*[]()~`>#+-=|{}.!"
        result = md(special)
        for ch in special:
            assert "\\" + ch in result

    def test_unicode_unchanged(self):
        assert md("złóż") == "złóż"

    def test_emoji_unchanged(self):
        assert md("🔒 ok") == "🔒 ok"

    def test_ip_address(self):
        result = md("192.168.1.1")
        assert result == r"192\.168\.1\.1"


class TestBold:
    def test_wraps_in_asterisks(self):
        result = bold("Status")
        assert result == "*Status*"

    def test_escapes_inner_text(self):
        result = bold("v1.2")
        assert result == r"*v1\.2*"


class TestCode:
    def test_wraps_in_backticks(self):
        assert code("DOWN") == "`DOWN`"

    def test_escapes_backtick_inside(self):
        result = code("a`b")
        assert "\\`" in result

    def test_ip_in_code(self):
        # w inline code nie escapujemy normalnych znakow MarkdownV2, tylko backtick/backslash
        result = code("192.168.1.1")
        assert "192.168.1.1" in result


class TestMonoBlock:
    def test_fenced_code(self):
        result = mono_block("print('hello')")
        assert result.startswith("```")
        assert result.endswith("```")
        assert "print" in result

    def test_with_lang(self):
        result = mono_block("x = 1", lang="python")
        assert result.startswith("```python")


class TestLink:
    def test_builds_link(self):
        result = link("Dashboard", "https://example.com")
        assert "[Dashboard]" in result
        assert "https://example\\.com" in result
