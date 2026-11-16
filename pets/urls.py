from django.urls import path

from . import views


app_name = "pets"

urlpatterns = [
    path("", views.pets_list, name="pets_list"),
    path("create/", views.pet_create, name="pet_create"),
    path("<int:pet_id>/edit/", views.pet_edit, name="pet_edit"),
    path("<int:pet_id>/", views.pet_detail, name="pet_detail"),
]
