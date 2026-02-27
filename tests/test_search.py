# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for origin_conversation_mcp.search."""
import os
from pathlib import Path

import pytest

from origin_conversation_mcp import search


class TestGetDbPath:
    """Tests for _get_db_path."""

    def test_uses_conversation_db_when_file_exists(self, temp_db):
        os.environ["CONVERSATION_DB"] = temp_db
        try:
            assert search._get_db_path() == temp_db
        finally:
            os.environ.pop("CONVERSATION_DB", None)

    def test_uses_origin_conversation_db_when_file_exists(self, temp_db):
        os.environ["ORIGIN_CONVERSATION_DB"] = temp_db
        try:
            assert search._get_db_path() == temp_db
        finally:
            os.environ.pop("ORIGIN_CONVERSATION_DB", None)

    def test_fallback_when_env_set_but_file_missing(self, tmp_path):
        # Put a real db in package db/ so fallback works
        repo_root = Path(search.__file__).resolve().parent.parent
        db_dir = repo_root / "db"
        db_dir.mkdir(exist_ok=True)
        dummy = db_dir / "dummy.db"
        dummy.touch()
        os.environ["CONVERSATION_DB"] = str(tmp_path / "nonexistent.db")
        try:
            path = search._get_db_path()
            assert path == str(dummy) or "db" in path
        finally:
            os.environ.pop("CONVERSATION_DB", None)

    def test_raises_when_no_db_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            search, "__file__", str(tmp_path / "origin_conversation_mcp" / "search.py")
        )
        os.environ["CONVERSATION_DB"] = str(tmp_path / "nope.db")
        try:
            with pytest.raises(FileNotFoundError, match="db/ directory not found"):
                search._get_db_path()
        finally:
            os.environ.pop("CONVERSATION_DB", None)


class TestParseIsoToFloat:
    """Tests for _parse_iso_to_float."""

    def test_none_or_empty_returns_none(self):
        assert search._parse_iso_to_float(None) is None
        assert search._parse_iso_to_float("") is None
        assert search._parse_iso_to_float("   ") is None

    def test_date_only_utc_start_of_day(self):
        ts = search._parse_iso_to_float("2024-01-15")
        assert ts is not None
        assert 1705276800 <= ts <= 1705363200  # 2024-01-15 00:00 UTC range

    def test_iso_with_z(self):
        ts = search._parse_iso_to_float("2024-01-15T12:00:00Z")
        assert ts is not None

    def test_invalid_returns_none(self):
        assert search._parse_iso_to_float("not-a-date") is None


class TestCreateTimeComparable:
    """Tests for _create_time_comparable."""

    def test_none_returns_none(self):
        assert search._create_time_comparable(None) is None

    def test_float_passthrough(self):
        assert search._create_time_comparable(1700000000.0) == 1700000000.0

    def test_int_passthrough(self):
        assert search._create_time_comparable(1700000000) == 1700000000.0

    def test_iso_string_parsed(self):
        ts = search._create_time_comparable("2024-01-15")
        assert ts is not None


class TestConversationSearch:
    """Tests for conversation_search."""

    def test_basic_search(self, temp_db):
        os.environ["CONVERSATION_DB"] = temp_db
        try:
            result = search.conversation_search(query="hello", limit=10)
            assert "hello" in result
            assert "user" in result
            assert "First chat" in result or "conv1" in result
        finally:
            os.environ.pop("CONVERSATION_DB", None)

    def test_filter_by_roles(self, temp_db):
        os.environ["CONVERSATION_DB"] = temp_db
        try:
            result = search.conversation_search(roles=["tool"], limit=10)
            assert "tool" in result
            assert "tool result" in result
        finally:
            os.environ.pop("CONVERSATION_DB", None)

    def test_date_range(self, temp_db):
        os.environ["CONVERSATION_DB"] = temp_db
        try:
            result = search.conversation_search(
                start_date="2023-11-01",
                end_date="2023-11-30",
                limit=10,
            )
            assert "No matching" in result or "---" in result
        finally:
            os.environ.pop("CONVERSATION_DB", None)

    def test_limit_clamping(self, temp_db):
        os.environ["CONVERSATION_DB"] = temp_db
        try:
            result = search.conversation_search(limit=1)
            assert result.count("---") <= 1
        finally:
            os.environ.pop("CONVERSATION_DB", None)

    def test_no_matches(self, temp_db):
        os.environ["CONVERSATION_DB"] = temp_db
        try:
            result = search.conversation_search(query="xyznonexistent", limit=10)
            assert result == "No matching messages."
        finally:
            os.environ.pop("CONVERSATION_DB", None)
