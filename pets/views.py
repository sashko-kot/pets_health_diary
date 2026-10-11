from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from homepage.views import page
from models.owners import find_owner_by_id
from models.pets import find_pet_by_id, format_weight
from storage import load_owners, load_pets, load_records


def pets_list(request):
    items = ""
    owners = load_owners()
    for pet in load_pets():
        owner = find_owner_by_id(owners, pet.owner_id)
        if owner is None:
            raise ValueError(
                f"Pet {pet.id} refers to missing owner {pet.owner_id}"
            )
        items += f"""
        <li class="list-group-item">
            <a href="{reverse('pet_detail', args=[pet.id])}">
                {escape(pet.name)}
            </a>
            — {escape(pet.species)}, хозяин: {escape(owner.name)}
            (ID {owner.id}),
            вес: {format_weight(pet.weight_kg)}
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Питомцев пока нет.</li>'

    content = f"""
    <h1>Мои питомцы</h1>
    <ul class="list-group mb-3">{items}</ul>
    <a href="/" class="btn btn-outline-secondary">На главную</a>
    """
    return HttpResponse(page("Питомцы", content))


def pet_detail(request, pet_id):
    pets = load_pets()
    pet = find_pet_by_id(pets, pet_id)
    if pet is None:
        content = """
        <h1 class="text-danger">Питомец не найден</h1>
        <a href="/pets/" class="btn btn-outline-secondary">
            ← К списку питомцев
        </a>
        """
        return HttpResponse(page("Питомец не найден", content), status=404)

    owner = find_owner_by_id(load_owners(), pet.owner_id)
    if owner is None:
        raise ValueError(
            f"Pet {pet.id} refers to missing owner {pet.owner_id}"
        )

    record_items = ""
    for record in load_records():
        if record.pet_id == pet.id:
            record_items += f"""
            <li class="list-group-item">
                <a href="{reverse('record_detail', args=[record.id])}">
                    {record.recorded_on:%d.%m.%Y}
                </a>
                — {escape(record.activity)}
            </li>
            """
    if not record_items:
        record_items = '<li class="list-group-item">Записей пока нет.</li>'

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(pet.name)}</h5>
            <p class="card-text"><strong>ID:</strong> {pet.id}</p>
            <p class="card-text">
                <strong>Вид:</strong> {escape(pet.species)}
            </p>
            <p class="card-text">
                <strong>Владелец:</strong> {escape(owner.name)}
                (ID {owner.id})
            </p>
            <p class="card-text">
                <strong>Вес:</strong> {format_weight(pet.weight_kg)}
            </p>
            <p class="card-text">
                <strong>Оценка веса:</strong> {escape(pet.weight_status)}
            </p>
            <h6>История здоровья</h6>
            <ul class="list-group mb-3">{record_items}</ul>
            <a href="/pets/" class="btn btn-outline-secondary">
                ← К списку питомцев
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Питомец: {pet.name}", content))
