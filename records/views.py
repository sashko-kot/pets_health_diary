from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

from models.pets import format_weight
from owners.models import Owner
from pets.models import Pet
from records.models import HealthRecord


def records_list(request):
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    pet_id = request.GET.get("pet", "").strip()
    owner_id = request.GET.get("owner", "").strip()
    sort = request.GET.get("sort", "date")
    error = None

    records = HealthRecord.objects.select_related("pet__owner")
    parsed_from = parse_date(date_from) if date_from else None
    parsed_to = parse_date(date_to) if date_to else None

    if (date_from and parsed_from is None) or (date_to and parsed_to is None):
        error = "Укажите корректный диапазон дат."
    elif parsed_from and parsed_to and parsed_from > parsed_to:
        error = "Начальная дата не может быть позже конечной."
    elif pet_id and not pet_id.isdigit():
        error = "Выберите питомца из списка."
    elif owner_id and not owner_id.isdigit():
        error = "Выберите хозяина из списка."

    if error:
        records = records.none()
    else:
        if parsed_from:
            records = records.filter(recorded_on__gte=parsed_from)
        if parsed_to:
            records = records.filter(recorded_on__lte=parsed_to)
        if pet_id:
            records = records.filter(pet_id=int(pet_id))
        if owner_id:
            records = records.filter(pet__owner_id=int(owner_id))

    sort_fields = {
        "date": ("-recorded_on", "-pk"),
        "pet": ("pet__name", "-recorded_on", "-pk"),
        "owner": ("pet__owner__name", "-recorded_on", "-pk"),
        "weight": ("-weight_kg", "-pk"),
    }
    if sort not in sort_fields:
        sort = "date"
    page_obj = Paginator(records.order_by(*sort_fields[sort]), 10).get_page(
        request.GET.get("page")
    )
    page_records = [
        _record_context(record)
        for record in page_obj.object_list
    ]
    context = {
        "records": page_records,
        "page_obj": page_obj,
        "total_records": page_obj.paginator.count,
        "pets": Pet.objects.order_by("name", "pk"),
        "owners": Owner.objects.order_by("name", "pk"),
        "date_from": date_from,
        "date_to": date_to,
        "selected_pet": pet_id,
        "selected_owner": owner_id,
        "sort": sort,
        "error": error,
    }
    return render(request, "records/records_list.html", context)


def _record_context(record):
    return {
        "record": record,
        "pet": record.pet,
        "owner": record.pet.owner,
        "weight_display": format_weight(record.weight_kg),
    }


def record_detail(request, record_id):
    try:
        record = get_object_or_404(
            HealthRecord.objects.select_related("pet__owner"),
            pk=record_id,
        )
    except Http404:
        return render(
            request,
            "records/record_detail.html",
            status=404,
        )
    context = _record_context(record)
    return render(request, "records/record_detail.html", context)


def records_search(request):
    symptom = request.GET.get("symptom", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    error = None
    records = HealthRecord.objects.select_related("pet__owner")
    parsed_from = parse_date(date_from) if date_from else None
    parsed_to = parse_date(date_to) if date_to else None

    if (date_from and parsed_from is None) or (date_to and parsed_to is None):
        error = "Укажите корректный диапазон дат."
        records = records.none()
    elif parsed_from and parsed_to and parsed_from > parsed_to:
        error = "Начальная дата не может быть позже конечной."
        records = records.none()
    elif symptom or parsed_from or parsed_to:
        if symptom:
            records = records.filter(symptoms__icontains=symptom)
        if parsed_from:
            records = records.filter(recorded_on__gte=parsed_from)
        if parsed_to:
            records = records.filter(recorded_on__lte=parsed_to)
    else:
        records = records.none()

    return render(request, "records/records_search.html", {
        "records": [
            _record_context(record)
            for record in records.order_by("-recorded_on", "-pk")
        ],
        "symptom": symptom,
        "date_from": date_from,
        "date_to": date_to,
        "error": error,
    })


def statistics(request):
    pet_stats = (
        Pet.objects.annotate(
            records_count=Count("health_records"),
            average_weight=Avg("health_records__weight_kg"),
            minimum_weight=Min("health_records__weight_kg"),
            maximum_weight=Max("health_records__weight_kg"),
        )
        .values(
            "id",
            "records_count",
            "average_weight",
            "minimum_weight",
            "maximum_weight",
            pet_name=F("name"),
        )
        .order_by("pet_name")
    )
    symptom_stats = (
        HealthRecord.objects.exclude(symptoms="")
        .values("symptoms")
        .annotate(records_count=Count("pk"))
        .filter(records_count__gte=1)
        .order_by("-records_count", "symptoms")
    )
    owner_stats = (
        Owner.objects.annotate(pets_count=Count("pets"))
        .values("id", "pets_count", owner_name=F("name"))
        .order_by("-pets_count", "owner_name")
    )
    record_summary = HealthRecord.objects.summary()
    return render(request, "records/statistics.html", {
        "pet_statistics": list(pet_stats),
        "symptom_statistics": list(symptom_stats),
        "owner_statistics": list(owner_stats),
        "record_summary": record_summary,
    })
