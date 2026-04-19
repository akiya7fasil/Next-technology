import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str
    password_hash: str


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.executescript(SCHEMA_SQL)


def get_user_by_email(db_path: Path, email: str) -> Optional[User]:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
        if not row:
            return None
        return User(
            id=int(row["id"]),
            name=str(row["name"]),
            email=str(row["email"]),
            password_hash=str(row["password_hash"]),
        )


def get_user_by_id(db_path: Path, user_id: int) -> Optional[User]:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE id = ?",
            (int(user_id),),
        ).fetchone()
        if not row:
            return None
        return User(
            id=int(row["id"]),
            name=str(row["name"]),
            email=str(row["email"]),
            password_hash=str(row["password_hash"]),
        )


def create_user(db_path: Path, name: str, email: str, password_hash: str) -> User:
    clean_email = email.strip().lower()
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Name is required")
    if not clean_email:
        raise ValueError("Email is required")
    if not password_hash:
        raise ValueError("Password hash is required")

    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (clean_name, clean_email, password_hash),
        )
        user_id = int(cur.lastrowid)
    user = get_user_by_id(db_path, user_id)
    if not user:
        raise RuntimeError("Failed to create user")
    return user


def update_user_password(db_path: Path, email: str, password_hash: str) -> bool:
    """Returns True if a row was updated."""
    clean = email.strip().lower()
    with _connect(db_path) as conn:
        cur = conn.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (password_hash, clean),
        )
        return cur.rowcount > 0

