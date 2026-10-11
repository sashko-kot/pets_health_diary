from django.urls import path

from . import views


urlpatterns = [
    path("", views.pets_list, name="pets_list"),
    path("<int:pet_id>/", views.pet_detail, name="pet_detail"),
]
