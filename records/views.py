from datetime import date
from types import SimpleNamespace

from django.shortcuts import render

from db.database import get_connection, load_queries
from models.owners import Owner
from models.pets import format_weight
from models.records import HealthRecord


def records_list(request):
    query = load_queries()["list_records"]
    with get_connection() as connection:
        rows = connection.execute(query).fetchall()
    context = {"records": [_record_context(row) for row in rows]}
    return render(request, "records/records_list.html", context)


def _record_context(row):
    record = HealthRecord(
        id=row["id"], pet_id=row["pet_id"],
        recorded_on=date.fromisoformat(row["recorded_on"]),
        activity=row["activity"], appetite=row["appetite"],
        symptoms=row["symptoms"], weight_kg=row["weight_kg"],
    )
    pet = SimpleNamespace(
        id=record.pet_id,
        name=row["pet_name"],
        species=row["species"],
    )
    owner = Owner(row["owner_id"], row["owner_name"], row["owner_email"])
    return {
        "record": record,
        "pet": pet,
        "owner": owner,
        "weight_display": format_weight(record.weight_kg),
    }


def record_detail(request, record_id):
    query = load_queries()["record_detail"]
    with get_connection() as connection:
        row = connection.execute(query, (record_id,)).fetchone()
    if row is None:
        return render(
            request,
            "records/record_detail.html",
            status=404,
        )

    context = _record_context(row)
    return render(request, "records/record_detail.html", context)


def records_search(request):
    symptom = request.GET.get("symptom", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    rows = []
    if date_from and date_to:
        query = load_queries()["records_in_date_range"]
        with get_connection() as connection:
            rows = connection.execute(query, (date_from, date_to)).fetchall()
    elif symptom:
        query = load_queries()["records_by_symptom"]
        with get_connection() as connection:
            rows = connection.execute(query, (f"%{symptom}%",)).fetchall()
    return render(request, "records/records_search.html", {
        "records": [_record_context(row) for row in rows],
        "symptom": symptom,
        "date_from": date_from,
        "date_to": date_to,
    })


def statistics(request):
    queries = load_queries()
    with get_connection() as connection:
        pet_stats = connection.execute(queries["pet_statistics"]).fetchall()
        symptom_stats = connection.execute(
            queries["symptom_statistics"], (1,)
        ).fetchall()
        owner_stats = connection.execute(
            queries["owner_pet_counts"]
        ).fetchall()
    return render(request, "records/statistics.html", {
        "pet_statistics": pet_stats,
        "symptom_statistics": symptom_stats,
        "owner_statistics": owner_stats,
    })
