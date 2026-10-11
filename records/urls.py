from django.urls import path

from . import views


app_name = "records"

urlpatterns = [
    path("", views.records_list, name="records_list"),
    path("<int:record_id>/", views.record_detail, name="record_detail"),
]
