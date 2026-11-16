"""Copy the legacy SQLite data into the database configured for Django."""

import os
import sqlite3
from datetime import date
from pathlib import Path

from django.apps import apps


BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "pets_health.sqlite"


def import_sqlite_to_orm(source_db: Path = SOURCE_DB) -> dict[str, int]:
    if not source_db.is_file():
        raise FileNotFoundError(f"Исходная база не найдена: {source_db}")

    if not apps.ready:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        import django

        django.setup()

    from django.db import transaction

    from owners.models import Owner
    from pets.models import Pet
    from records.models import HealthRecord

    with sqlite3.connect(source_db) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
        if violations:
            raise ValueError(
                f"В исходной базе нарушены внешние ключи: {violations!r}"
            )

        owners = connection.execute(
            "SELECT id, name, email FROM owners ORDER BY id"
        ).fetchall()
        pets = connection.execute(
            """
            SELECT id, name, species, owner_id, weight_kg,
                   recommended_weight_kg
            FROM pets
            ORDER BY id
            """
        ).fetchall()
        records = connection.execute(
            """
            SELECT id, pet_id, recorded_on, activity, appetite,
                   symptoms, weight_kg
            FROM health_records
            ORDER BY id
            """
        ).fetchall()

    with transaction.atomic():
        for row in owners:
            Owner.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "email": row["email"],
                },
            )

        for row in pets:
            Pet.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "species": row["species"],
                    "owner_id": row["owner_id"],
                    "weight_kg": float(row["weight_kg"]),
                    "recommended_weight_kg": float(
                        row["recommended_weight_kg"]
                    ),
                },
            )

        for row in records:
            HealthRecord.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "pet_id": row["pet_id"],
                    "recorded_on": date.fromisoformat(row["recorded_on"]),
                    "activity": row["activity"],
                    "appetite": row["appetite"],
                    "symptoms": row["symptoms"],
                    "weight_kg": float(row["weight_kg"]),
                },
            )

    counts: dict[str, int] = {
        "owners": Owner.objects.count(),
        "pets": Pet.objects.count(),
        "health_records": HealthRecord.objects.count(),
    }
    return counts


def main() -> None:
    counts = import_sqlite_to_orm()
    print(
        "Перенос завершён: "
        f"{counts['owners']} хозяев, {counts['pets']} питомцев, "
        f"{counts['health_records']} записей."
    )


if __name__ == "__main__":
    main()
