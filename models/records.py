from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class HealthRecord:
    id: int
    pet_id: int
    recorded_on: date
    activity: str
    appetite: str
    symptoms: str
    weight_kg: float

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "HealthRecord":
        return cls(
            id=int(data["id"]),
            pet_id=int(data["pet_id"]),
            recorded_on=date.fromisoformat(str(data["recorded_on"])),
            activity=str(data["activity"]),
            appetite=str(data["appetite"]),
            symptoms=str(data["symptoms"]),
            weight_kg=float(data["weight_kg"]),
        )

    @property
    def info(self) -> str:
        return (
            f"{self.recorded_on:%d.%m.%Y}: {self.activity}, "
            f"аппетит: {self.appetite}, симптомы: {self.symptoms}, "
            f"вес: {self.weight_kg:.3f} кг"
        )

    def __str__(self) -> str:
        return f"{self.id}: питомец ID {self.pet_id}, {self.info}"


def add_record(
    records: list[HealthRecord],
    pet_id: int,
    recorded_on: date,
    activity: str,
    appetite: str,
    symptoms: str,
    weight_kg: float,
) -> HealthRecord:
    record = HealthRecord(
        id=max((item.id for item in records), default=0) + 1,
        pet_id=pet_id,
        recorded_on=recorded_on,
        activity=activity.strip(),
        appetite=appetite.strip(),
        symptoms=symptoms.strip(),
        weight_kg=weight_kg,
    )
    records.append(record)
    return record


def find_record_by_id(
    records: list[HealthRecord],
    record_id: int,
) -> HealthRecord | None:
    for record in records:
        if record.id == record_id:
            return record
    return None


def find_records_by_pet_id(
    records: list[HealthRecord],
    pet_id: int,
) -> list[HealthRecord]:
    return [record for record in records if record.pet_id == pet_id]


def sort_records(
    records: list[HealthRecord],
    newest_first: bool = True,
) -> list[HealthRecord]:
    return sorted(
        records,
        key=lambda record: (record.recorded_on, record.id),
        reverse=newest_first,
    )


def show_records(records: list[HealthRecord]) -> None:
    for record in records:
        print(record)
