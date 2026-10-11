from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from homepage.views import page
from models.owners import find_owner_by_id
from models.pets import find_pet_by_id, format_weight
from models.records import find_record_by_id
from storage import load_owners, load_pets, load_records


def records_list(request):
    pets = load_pets()
    owners = load_owners()
    items = ""
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
        items += f"""
        <li class="list-group-item">
            <a href="{reverse('record_detail', args=[record.id])}">
                Запись от {record.recorded_on:%d.%m.%Y}
            </a>
            — {escape(pet.name)}
            (хозяин: {escape(owner.name)}, ID {owner.id}):
            {escape(record.activity)}, аппетит —
            {escape(record.appetite)}
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Записей пока нет.</li>'

    content = f"""
    <h1>Дневник здоровья</h1>
    <ul class="list-group mb-3">{items}</ul>
    <a href="/" class="btn btn-outline-secondary">На главную</a>
    """
    return HttpResponse(page("Дневник здоровья", content))


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
        content = """
        <h1 class="text-danger">Запись не найдена</h1>
        <a href="/records/" class="btn btn-outline-secondary">
            ← К списку записей
        </a>
        """
        return HttpResponse(page("Запись не найдена", content), status=404)

    pet, owner = _pet_and_owner_for_record(record)

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Осмотр питомца {escape(pet.name)}</h5>
            <p class="card-text">
                <strong>Хозяин:</strong> {escape(owner.name)} (ID {owner.id})
            </p>
            <p class="card-text"><strong>Запись №:</strong> {record.id}</p>
            <p class="card-text">
                <strong>Дата:</strong> {record.recorded_on:%d.%m.%Y}
            </p>
            <p class="card-text">
                <strong>Активность:</strong> {escape(record.activity)}
            </p>
            <p class="card-text">
                <strong>Аппетит:</strong> {escape(record.appetite)}
            </p>
            <p class="card-text">
                <strong>Симптомы:</strong> {escape(record.symptoms)}
            </p>
            <p class="card-text">
                <strong>Вес:</strong> {format_weight(record.weight_kg)}
            </p>
            <a href="{reverse('pet_detail', args=[pet.id])}"
               class="btn btn-outline-primary">Карточка питомца</a>
            <a href="/records/" class="btn btn-outline-secondary">
                ← К списку записей
            </a>
        </div>
    </div>
    """
    title = f"Запись от {record.recorded_on:%d.%m.%Y}"
    return HttpResponse(page(title, content))
