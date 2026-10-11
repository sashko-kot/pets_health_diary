from django.shortcuts import render

from storage import load_pets, load_records


def index(request):
    context = {
        "pet_count": len(load_pets()),
        "record_count": len(load_records()),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    return render(
        request,
        "homepage/404.html",
        status=404,
    )
