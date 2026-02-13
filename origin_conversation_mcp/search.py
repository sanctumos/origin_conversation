# SPDX-License-Identifier: AGPL-3.0-only
# origin_conversation - Conversation search over canonical ChatGPT export DB.
"""
Search canonical conversation DB: text filter, role filter, date range, limit.
Returns formatted message list with timestamps and content.
"""
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _get_db_path() -> str:
    """Resolve path to canonical export SQLite DB."""
    env_path = os.environ.get("CONVERSATION_DB") or os.environ.get("ORIGIN_CONVERSATION_DB")
    if env_path and os.path.isfile(env_path):
        return env_path
    base = Path(__file__).resolve().parent.parent
    db_dir = base / "db"
    if not db_dir.is_dir():
        raise FileNotFoundError(f"db/ directory not found: {db_dir}")
    candidates = sorted(db_dir.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No *.db file in {db_dir}")
    return str(candidates[0])


def _parse_iso_to_float(s: str | None) -> float | None:
    """Convert ISO 8601 date/datetime string to Unix timestamp (float) for comparison."""
    if not s or not s.strip():
        return None
    s = s.strip()
    # Date only -> start of day UTC
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        s = s + "T00:00:00"
    # Optional timezone: assume Z or no suffix = UTC
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    if "T" in s and "+" not in s and "Z" not in s and s[-1] != "Z":
        s = s + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except (ValueError, TypeError):
        return None


def _create_time_comparable(create_time: Any) -> float | None:
    """Convert DB create_time (str or number) to float for range comparison."""
    if create_time is None:
        return None
    if isinstance(create_time, (int, float)):
        return float(create_time)
    s = str(create_time).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        pass
    return _parse_iso_to_float(s)


def conversation_search(
    *,
    query: str | None = None,
    roles: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
) -> str:
    """
    Search canonical conversation DB. All parameters optional.
    - query: text to match in message content (and conversation title)
    - roles: filter by role: user, assistant, tool (or combinations)
    - start_date, end_date: ISO 8601 inclusive range
    - limit: max results (default 50)
    """
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        sql = """
            SELECT m.id, m.conversation_id, m.role, m.content, m.create_time, m.position,
                   c.title AS conversation_title
            FROM messages m
            JOIN conversations c ON c.id = m.conversation_id
            WHERE 1=1
        """
        params: list[Any] = []

        if query and query.strip():
            q = f"%{query.strip()}%"
            sql += " AND (m.content LIKE ? OR c.title LIKE ?)"
            params.extend([q, q])

        if roles:
            placeholders = ",".join("?" * len(roles))
            sql += f" AND m.role IN ({placeholders})"
            params.extend(roles)

        sql += " ORDER BY m.create_time DESC"
        fetch_limit = 5000 if (start_date or end_date) else min(limit * 3, 500)
        sql += " LIMIT ?"
        params.append(fetch_limit)

        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()

        start_ts = _parse_iso_to_float(start_date) if start_date else None
        end_ts = _parse_iso_to_float(end_date) if end_date else None
        if end_ts is not None and end_date and re.match(r"^\d{4}-\d{2}-\d{2}$", end_date.strip()):
            # Inclusive full day: end of day
            end_ts = end_ts + 86400 - 0.001

        out: list[str] = []
        for row in rows:
            ct = _create_time_comparable(row["create_time"])
            if start_ts is not None and (ct is None or ct < start_ts):
                continue
            if end_ts is not None and (ct is None or ct > end_ts):
                continue
            if len(out) >= limit:
                break
            ts = row["create_time"]
            if ts is not None:
                try:
                    t = float(ts)
                    dt = datetime.fromtimestamp(t, tz=timezone.utc)
                    ts = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError, OSError):
                    ts = str(ts)
            else:
                ts = "(no time)"
            role = row["role"] or "unknown"
            content = (row["content"] or "").strip()
            if len(content) > 2000:
                content = content[:2000] + "..."
            title = (row["conversation_title"] or "").strip() or row["conversation_id"][:8]
            out.append(f"[{ts}] {role} (conv: {title})\n{content}")
        return "\n\n---\n\n".join(out) if out else "No matching messages."
    finally:
        conn.close()
