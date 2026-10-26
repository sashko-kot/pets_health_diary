from datetime import date

from django.shortcuts import render

from db.database import get_connection, load_queries
from models.owners import Owner
from models.pets import Pet, format_weight
from models.records import HealthRecord


def pets_list(request):
    queries = load_queries()
    species = request.GET.get("species", "").strip()
    query = queries["pets_by_species"] if species else queries["list_pets"]
    with get_connection() as connection:
        rows = connection.execute(
            query, (f"%{species}%",) if species else ()
        ).fetchall()
    pets = []
    for row in rows:
        pet = Pet(
            id=row["id"], name=row["name"], species=row["species"],
            owner_id=row["owner_id"], weight_kg=row["weight_kg"],
            recommended_weight_kg=row["recommended_weight_kg"],
        )
        pets.append({
            "pet": pet,
            "owner": Owner(
                row["owner_id"], row["owner_name"], row["owner_email"]
            ),
            "weight_display": format_weight(pet.weight_kg),
        })

    context = {"pets": pets, "species": species}
    return render(request, "pets/pets_list.html", context)


def pet_detail(request, pet_id):
    queries = load_queries()
    with get_connection() as connection:
        row = connection.execute(queries["pet_detail"], (pet_id,)).fetchone()
        record_rows = (
            connection.execute(queries["pet_records"], (pet_id,)).fetchall()
            if row else []
        )
    if row is None:
        return render(
            request,
            "pets/pet_detail.html",
            status=404,
        )

    pet = Pet(
        id=row["id"], name=row["name"], species=row["species"],
        owner_id=row["owner_id"], weight_kg=row["weight_kg"],
        recommended_weight_kg=row["recommended_weight_kg"],
    )
    owner = Owner(row["owner_id"], row["owner_name"], row["owner_email"])
    records = []
    for record_row in record_rows:
        record = HealthRecord(
            id=record_row["id"], pet_id=record_row["pet_id"],
            recorded_on=date.fromisoformat(record_row["recorded_on"]),
            activity=record_row["activity"], appetite=record_row["appetite"],
            symptoms=record_row["symptoms"], weight_kg=record_row["weight_kg"],
        )
        records.append({
            "record": record,
            "weight_display": format_weight(record.weight_kg),
        })

    context = {
        "pet": pet,
        "owner": owner,
        "weight_display": format_weight(pet.weight_kg),
        "records": records,
    }
    return render(request, "pets/pet_detail.html", context)
