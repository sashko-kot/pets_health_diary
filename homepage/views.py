from django.shortcuts import render

from pets.models import Pet
from records.models import HealthRecord


def index(request):
    context = {
        "pet_count": Pet.objects.count(),
        "record_count": HealthRecord.objects.count(),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    return render(
        request,
        "homepage/404.html",
        status=404,
    )
