import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from models.owners import Owner
from models.pets import Pet
from models.records import HealthRecord


DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_rows(filename: str) -> list[dict[str, Any]]:
    file_path = DATA_DIR / filename
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{file_path} must contain a JSON list")

    rows = []
    for row in data:
        if not isinstance(row, dict):
            raise ValueError(
                f"Each entry in {file_path} must be a JSON object"
            )
        rows.append(row)
    return rows


def load_pets() -> list[Pet]:
    return [Pet(**row) for row in _load_rows("pets.json")]


def load_owners() -> list[Owner]:
    return [Owner.from_data(row) for row in _load_rows("owners.json")]


def load_records() -> list[HealthRecord]:
    return [
        HealthRecord.from_data(row)
        for row in _load_rows("records.json")
    ]


def _save_rows(filename: str, rows: list[dict[str, Any]]) -> None:
    file_path = DATA_DIR / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
    temporary_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(file_path)


def save_owners(owners: list[Owner]) -> None:
    _save_rows("owners.json", [asdict(owner) for owner in owners])


def save_pets(pets: list[Pet]) -> None:
    _save_rows("pets.json", [asdict(pet) for pet in pets])


def save_records(records: list[HealthRecord]) -> None:
    rows = []
    for record in records:
        row = asdict(record)
        row["recorded_on"] = record.recorded_on.isoformat()
        rows.append(row)
    _save_rows("records.json", rows)
