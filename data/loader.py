from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MOCK_DATA_DIR = PROJECT_ROOT / "mock_data"
DB_PATH = PROJECT_ROOT / "data" / "procurement_data.sqlite3"

_TABLE_TO_FILE = {
    "vendors": "vendors.json",
    "policies": "policies.json",
    "budgets": "budgets.json",
    "requests": "requests.json",
}


def _mock_files_mtime() -> float:
    return max((MOCK_DATA_DIR / filename).stat().st_mtime for filename in _TABLE_TO_FILE.values())


def _database_is_stale() -> bool:
    if not DB_PATH.exists():
        return True
    return DB_PATH.stat().st_mtime < _mock_files_mtime()


def _rebuild_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        for table in _TABLE_TO_FILE:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            cursor.execute(
                f"""
                CREATE TABLE {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_index INTEGER NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

            file_path = MOCK_DATA_DIR / _TABLE_TO_FILE[table]
            with file_path.open("r", encoding="utf-8") as file:
                records = json.load(file)

            if not isinstance(records, list):
                raise ValueError(f"Expected list data in {_TABLE_TO_FILE[table]}")

            cursor.executemany(
                f"INSERT INTO {table} (source_index, payload) VALUES (?, ?)",
                [(index, json.dumps(record)) for index, record in enumerate(records)],
            )

        connection.commit()


def _ensure_database() -> None:
    if _database_is_stale():
        _rebuild_database()


def _load_table(table_name: str) -> list[dict[str, Any]]:
    """Load records from the SQLite mock-data store and return list records."""

    _ensure_database()

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        rows = cursor.execute(
            f"SELECT payload FROM {table_name} ORDER BY source_index ASC"
        ).fetchall()

    records: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(row[0])
        if not isinstance(payload, dict):
            raise ValueError(f"Expected object records in table {table_name}")
        records.append(payload)

    return records


def load_vendors() -> list[dict[str, Any]]:
    """Load vendor records from the SQLite-backed mock data store."""

    return _load_table("vendors")


def load_policies() -> list[dict[str, Any]]:
    """Load policy records from the SQLite-backed mock data store."""

    return _load_table("policies")


def load_budgets() -> list[dict[str, Any]]:
    """Load budget records from the SQLite-backed mock data store."""

    return _load_table("budgets")


def load_requests() -> list[dict[str, Any]]:
    """Load purchase request records from the SQLite-backed mock data store."""

    return _load_table("requests")
