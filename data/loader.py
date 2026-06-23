from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MOCK_DATA_DIR = PROJECT_ROOT / "mock_data"


def _load_json(filename: str) -> list[dict[str, Any]]:
    """Load a mock-data JSON file from the project root and return list records."""

    file_path = MOCK_DATA_DIR / filename
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"Expected list data in {filename}")
    return data


def load_vendors() -> list[dict[str, Any]]:
    """Load vendor records from mock_data/vendors.json."""

    return _load_json("vendors.json")


def load_policies() -> list[dict[str, Any]]:
    """Load policy records from mock_data/policies.json."""

    return _load_json("policies.json")


def load_budgets() -> list[dict[str, Any]]:
    """Load budget records from mock_data/budgets.json."""

    return _load_json("budgets.json")


def load_requests() -> list[dict[str, Any]]:
    """Load purchase request records from mock_data/requests.json."""

    return _load_json("requests.json")
