from django.urls import path, register_converter

from .converters import UnicodeSlugConverter
from . import views


register_converter(UnicodeSlugConverter, "unicode_slug")

app_name = "pets"

urlpatterns = [
    path("", views.pets_list, name="pets_list"),
    path("<int:pet_id>/", views.pet_detail, name="pet_detail"),
    path(
        "<unicode_slug:slug>/",
        views.pet_detail_by_slug,
        name="pet_detail_by_slug",
    ),
]
