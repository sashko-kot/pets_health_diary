from django.urls import path

from . import views


app_name = "records"

urlpatterns = [
    path("", views.records_list, name="records_list"),
    path("search/", views.records_search, name="records_search"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:record_id>/", views.record_detail, name="record_detail"),
]
