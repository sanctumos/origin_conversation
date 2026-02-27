# SPDX-License-Identifier: AGPL-3.0-only
"""Pytest fixtures for origin_conversation_mcp tests."""
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_db(tmp_path):
    """Create a minimal canonical-export-style SQLite DB with conversations and messages."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE conversations (id TEXT PRIMARY KEY, title TEXT)"
    )
    conn.execute(
        """CREATE TABLE messages (
            id TEXT, conversation_id TEXT, role TEXT, content TEXT,
            create_time REAL, position INTEGER,
            FOREIGN KEY(conversation_id) REFERENCES conversations(id)
        )"""
    )
    conn.execute(
        "INSERT INTO conversations (id, title) VALUES (?, ?)",
        ("conv1", "First chat"),
    )
    conn.execute(
        "INSERT INTO conversations (id, title) VALUES (?, ?)",
        ("conv2", "Second chat"),
    )
    # create_time as Unix timestamp (float)
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, create_time, position) VALUES (?, ?, ?, ?, ?, ?)",
        ("m1", "conv1", "user", "hello world", 1700000000.0, 0),
    )
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, create_time, position) VALUES (?, ?, ?, ?, ?, ?)",
        ("m2", "conv1", "assistant", "hi there", 1700000060.0, 1),
    )
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, create_time, position) VALUES (?, ?, ?, ?, ?, ?)",
        ("m3", "conv2", "user", "foo bar", 1700001000.0, 0),
    )
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, create_time, position) VALUES (?, ?, ?, ?, ?, ?)",
        ("m4", "conv2", "tool", "tool result", 1700001060.0, 1),
    )
    conn.commit()
    conn.close()
    return str(db_path)
