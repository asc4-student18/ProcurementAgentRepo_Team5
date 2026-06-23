from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MOCK_DATA_DIR = Path(__file__).resolve().parent.parent / "mock_data"


def _load_json(filename: str) -> list[dict[str, Any]]:
    file_path = MOCK_DATA_DIR / filename
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"Expected list data in {filename}")
    return data


def load_vendors() -> list[dict[str, Any]]:
    return _load_json("vendors.json")


def load_policies() -> list[dict[str, Any]]:
    return _load_json("policies.json")


def load_budgets() -> list[dict[str, Any]]:
    return _load_json("budgets.json")
