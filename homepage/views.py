from django.shortcuts import render

from db.database import get_connection, load_queries


def index(request):
    query = load_queries()["total_counts"]
    with get_connection() as connection:
        counts = connection.execute(query).fetchone()
    context = {
        "pet_count": counts["pet_count"],
        "record_count": counts["record_count"],
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    return render(
        request,
        "homepage/404.html",
        status=404,
    )
