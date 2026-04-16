"""SQLite database for storing user sessions and reserve state."""

import sqlite3
import time
import logging
from contextlib import contextmanager

from config import DATABASE_PATH
from crypto import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)


def _migrate_db(conn):
    """Add columns that may not exist in older databases."""
    cursor = conn.execute("PRAGMA table_info(chats)")
    columns = {row[1] for row in cursor.fetchall()}
    if "utc_offset" not in columns:
        conn.execute("ALTER TABLE chats ADD COLUMN utc_offset REAL NOT NULL DEFAULT 0")
    if "timezone_name" not in columns:
        conn.execute("ALTER TABLE chats ADD COLUMN timezone_name TEXT")


def init_db():
    """Create tables if they don't exist."""
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id         INTEGER PRIMARY KEY,
                language        TEXT    NOT NULL DEFAULT 'en',
                region          TEXT,
                account_id      INTEGER,
                nickname        TEXT,
                access_token    TEXT,
                token_expires   INTEGER,
                clan_id         INTEGER,
                utc_offset      REAL    NOT NULL DEFAULT 0,
                timezone_name   TEXT,
                is_active       INTEGER NOT NULL DEFAULT 1,
                token_warning_sent INTEGER NOT NULL DEFAULT 0,
                created_at      INTEGER NOT NULL,
                updated_at      INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS auth_states (
                state           TEXT    PRIMARY KEY,
                chat_id         INTEGER NOT NULL,
                created_at      INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notified_reserves (
                chat_id         INTEGER NOT NULL,
                reserve_key     TEXT    NOT NULL,
                notified_at     INTEGER NOT NULL,
                PRIMARY KEY (chat_id, reserve_key)
            );
            """
        )
        _migrate_db(conn)


@contextmanager
def _connect():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Chat operations ─────────────────────────────────────────────

def upsert_chat(chat_id: int, **fields):
    """Insert or update a chat record. Encrypts access_token before storing."""
    now = int(time.time())
    # Encrypt token if provided
    if "access_token" in fields and fields["access_token"] is not None:
        fields["access_token"] = encrypt_token(fields["access_token"])
    with _connect() as conn:
        existing = conn.execute("SELECT 1 FROM chats WHERE chat_id = ?", (chat_id,)).fetchone()
        if existing:
            sets = ", ".join(f"{k} = ?" for k in fields)
            vals = list(fields.values()) + [now, chat_id]
            conn.execute(f"UPDATE chats SET {sets}, updated_at = ? WHERE chat_id = ?", vals)
        else:
            fields.setdefault("language", "en")
            fields["chat_id"] = chat_id
            fields["created_at"] = now
            fields["updated_at"] = now
            cols = ", ".join(fields.keys())
            placeholders = ", ".join("?" for _ in fields)
            conn.execute(f"INSERT INTO chats ({cols}) VALUES ({placeholders})", list(fields.values()))


def _decrypt_chat(row: dict) -> dict:
    """Decrypt access_token in a chat record."""
    if row.get("access_token"):
        row["access_token"] = decrypt_token(row["access_token"])
    return row


def get_chat(chat_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,)).fetchone()
        return _decrypt_chat(dict(row)) if row else None


def get_active_chats() -> list[dict]:
    """Get all chats that have a valid token and are active."""
    now = int(time.time())
    with _connect() as conn:
        rows = conn.execute(
            """SELECT * FROM chats
               WHERE is_active = 1
                 AND access_token IS NOT NULL
                 AND token_expires > ?""",
            (now,),
        ).fetchall()
        return [_decrypt_chat(dict(r)) for r in rows]


def get_chats_with_expiring_tokens() -> list[dict]:
    """Get chats whose tokens expire within TOKEN_EXPIRY_WARNING seconds."""
    from config import TOKEN_EXPIRY_WARNING
    now = int(time.time())
    with _connect() as conn:
        rows = conn.execute(
            """SELECT * FROM chats
               WHERE is_active = 1
                 AND access_token IS NOT NULL
                 AND token_expires > ?
                 AND token_expires < ?
                 AND token_warning_sent = 0""",
            (now, now + TOKEN_EXPIRY_WARNING),
        ).fetchall()
        return [_decrypt_chat(dict(r)) for r in rows]


def get_chats_with_expired_tokens() -> list[dict]:
    """Get chats whose tokens have just expired (within last poll cycle)."""
    now = int(time.time())
    with _connect() as conn:
        rows = conn.execute(
            """SELECT * FROM chats
               WHERE is_active = 1
                 AND access_token IS NOT NULL
                 AND token_expires <= ?
                 AND token_expires > ?""",
            (now, now - 300),
        ).fetchall()
        return [_decrypt_chat(dict(r)) for r in rows]


def deactivate_chat(chat_id: int):
    upsert_chat(chat_id, is_active=0, access_token=None)


def delete_chat(chat_id: int):
    """Permanently delete all data for a chat."""
    with _connect() as conn:
        conn.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        conn.execute("DELETE FROM auth_states WHERE chat_id = ?", (chat_id,))
        conn.execute("DELETE FROM notified_reserves WHERE chat_id = ?", (chat_id,))


# ── Auth state operations ───────────────────────────────────────

def save_auth_state(state: str, chat_id: int):
    now = int(time.time())
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO auth_states (state, chat_id, created_at) VALUES (?, ?, ?)",
            (state, chat_id, now),
        )


def pop_auth_state(state: str) -> int | None:
    """Get and delete the chat_id for a given auth state."""
    with _connect() as conn:
        row = conn.execute("SELECT chat_id FROM auth_states WHERE state = ?", (state,)).fetchone()
        if row:
            conn.execute("DELETE FROM auth_states WHERE state = ?", (state,))
            return row["chat_id"]
        return None


def cleanup_old_auth_states():
    """Remove auth states older than 10 minutes."""
    cutoff = int(time.time()) - 600
    with _connect() as conn:
        conn.execute("DELETE FROM auth_states WHERE created_at < ?", (cutoff,))


# ── Notified reserves tracking ──────────────────────────────────

def was_reserve_notified(chat_id: int, reserve_key: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM notified_reserves WHERE chat_id = ? AND reserve_key = ?",
            (chat_id, reserve_key),
        ).fetchone()
        return row is not None


def mark_reserve_notified(chat_id: int, reserve_key: str):
    now = int(time.time())
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO notified_reserves (chat_id, reserve_key, notified_at) VALUES (?, ?, ?)",
            (chat_id, reserve_key, now),
        )


def cleanup_old_notifications():
    """Remove notification records older than 24 hours."""
    cutoff = int(time.time()) - 86400
    with _connect() as conn:
        conn.execute("DELETE FROM notified_reserves WHERE notified_at < ?", (cutoff,))
