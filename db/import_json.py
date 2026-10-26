"""Import the original JSON data into the SQLite database."""

import json

from db.database import DB_PATH, initialize_database, get_connection
from storage import DATA_DIR


def import_json() -> None:
    owners_path = DATA_DIR / "owners.json"
    pets_path = DATA_DIR / "pets.json"
    records_path = DATA_DIR / "records.json"
    owners = json.loads(owners_path.read_text(encoding="utf-8"))
    pets = json.loads(pets_path.read_text(encoding="utf-8"))
    records = json.loads(records_path.read_text(encoding="utf-8"))

    initialize_database()
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO owners (id, name, email) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                email = excluded.email
            """,
            [(row["id"], row["name"], row["email"]) for row in owners],
        )
        connection.executemany(
            """
            INSERT INTO pets (
                id, name, species, owner_id, weight_kg, recommended_weight_kg
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                species = excluded.species,
                owner_id = excluded.owner_id,
                weight_kg = excluded.weight_kg,
                recommended_weight_kg = excluded.recommended_weight_kg
            """,
            [
                (
                    row["id"], row["name"], row["species"], row["owner_id"],
                    row["weight_kg"], row["recommended_weight_kg"],
                )
                for row in pets
            ],
        )
        connection.executemany(
            """
            INSERT INTO health_records (
                id, pet_id, recorded_on, activity, appetite, symptoms,
                weight_kg
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                pet_id = excluded.pet_id,
                recorded_on = excluded.recorded_on,
                activity = excluded.activity,
                appetite = excluded.appetite,
                symptoms = excluded.symptoms,
                weight_kg = excluded.weight_kg
            """,
            [
                (
                    row["id"], row["pet_id"], row["recorded_on"],
                    row["activity"], row["appetite"], row["symptoms"],
                    row["weight_kg"],
                )
                for row in records
            ],
        )
    print(
        f"Imported {len(owners)} owners, {len(pets)} pets, "
        f"and {len(records)} health records into {DB_PATH}."
    )


if __name__ == "__main__":
    import_json()
