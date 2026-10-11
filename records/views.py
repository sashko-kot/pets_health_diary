from django.shortcuts import render

from models.owners import find_owner_by_id
from models.pets import find_pet_by_id, format_weight
from models.records import find_record_by_id
from storage import load_owners, load_pets, load_records


def records_list(request):
    pets = load_pets()
    owners = load_owners()
    records = []
    for record in load_records():
        pet = find_pet_by_id(pets, record.pet_id)
        if pet is None:
            raise ValueError(
                f"Health record {record.id} refers to missing pet "
                f"{record.pet_id}"
            )
        owner = find_owner_by_id(owners, pet.owner_id)
        if owner is None:
            raise ValueError(
                f"Pet {pet.id} refers to missing owner {pet.owner_id}"
            )
        records.append(
            {
                "record": record,
                "pet": pet,
                "owner": owner,
                "weight_display": format_weight(record.weight_kg),
            }
        )

    context = {"records": records}
    return render(request, "records/records_list.html", context)


def _pet_and_owner_for_record(record):
    pet = find_pet_by_id(load_pets(), record.pet_id)
    if pet is None:
        raise ValueError(
            f"Health record {record.id} refers to missing pet {record.pet_id}"
        )
    owner = find_owner_by_id(load_owners(), pet.owner_id)
    if owner is None:
        raise ValueError(
            f"Pet {pet.id} refers to missing owner {pet.owner_id}"
        )
    return pet, owner


def record_detail(request, record_id):
    record = find_record_by_id(load_records(), record_id)
    if record is None:
        return render(
            request,
            "records/record_detail.html",
            status=404,
        )

    pet, owner = _pet_and_owner_for_record(record)
    context = {
        "record": record,
        "pet": pet,
        "owner": owner,
        "weight_display": format_weight(record.weight_kg),
    }
    return render(request, "records/record_detail.html", context)
