from django.http import Http404
from django.shortcuts import get_object_or_404, render

from models.pets import format_weight
from pets.models import Pet


def pets_list(request):
    species = request.GET.get("species", "").strip()
    pets = Pet.objects.select_related("owner")
    if species:
        pets = pets.filter(species__icontains=species)

    context = {
        "pets": [
            {
                "pet": pet,
                "owner": pet.owner,
                "weight_display": format_weight(pet.weight_kg),
            }
            for pet in pets
        ],
        "species": species,
    }
    return render(request, "pets/pets_list.html", context)


def pet_detail(request, pet_id):
    try:
        pet = get_object_or_404(
            Pet.objects.select_related("owner").prefetch_related(
                "health_records"
            ),
            pk=pet_id,
        )
    except Http404:
        return render(request, "pets/pet_detail.html", status=404)
    return _render_pet_detail(request, pet)


def pet_detail_by_slug(request, slug):
    try:
        pet = get_object_or_404(
            Pet.objects.select_related("owner").prefetch_related(
                "health_records"
            ),
            slug=slug,
        )
    except Http404:
        return render(request, "pets/pet_detail.html", status=404)
    return _render_pet_detail(request, pet)


def _render_pet_detail(request, pet):
    records = [
        {
            "record": record,
            "weight_display": format_weight(record.weight_kg),
        }
        for record in pet.health_records.all()
    ]
    context = {
        "pet": pet,
        "owner": pet.owner,
        "weight_display": format_weight(pet.weight_kg),
        "records": records,
    }
    return render(request, "pets/pet_detail.html", context)
