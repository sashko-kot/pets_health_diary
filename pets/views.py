from django.shortcuts import render

from models.owners import find_owner_by_id
from models.pets import find_pet_by_id, format_weight
from storage import load_owners, load_pets, load_records


def pets_list(request):
    owners = load_owners()
    pets = []
    for pet in load_pets():
        owner = find_owner_by_id(owners, pet.owner_id)
        if owner is None:
            raise ValueError(
                f"Pet {pet.id} refers to missing owner {pet.owner_id}"
            )
        pets.append(
            {
                "pet": pet,
                "owner": owner,
                "weight_display": format_weight(pet.weight_kg),
            }
        )

    context = {"pets": pets}
    return render(request, "pets/pets_list.html", context)


def pet_detail(request, pet_id):
    pets = load_pets()
    pet = find_pet_by_id(pets, pet_id)
    if pet is None:
        return render(
            request,
            "pets/pet_detail.html",
            status=404,
        )

    owner = find_owner_by_id(load_owners(), pet.owner_id)
    if owner is None:
        raise ValueError(
            f"Pet {pet.id} refers to missing owner {pet.owner_id}"
        )

    records = []
    for record in load_records():
        if record.pet_id == pet.id:
            records.append(
                {
                    "record": record,
                    "weight_display": format_weight(record.weight_kg),
                }
            )

    context = {
        "pet": pet,
        "owner": owner,
        "weight_display": format_weight(pet.weight_kg),
        "records": records,
    }
    return render(request, "pets/pet_detail.html", context)
