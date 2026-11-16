from django.contrib import admin

from .models import HealthRecord


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = (
        "recorded_on",
        "pet",
        "owner_name",
        "activity",
        "appetite",
        "weight_kg",
    )
    list_filter = ("recorded_on", "pet__species")
    search_fields = (
        "pet__name",
        "pet__owner__name",
        "pet__owner__email",
        "symptoms",
    )
    date_hierarchy = "recorded_on"
    ordering = ("-recorded_on", "-pk")
    list_select_related = ("pet", "pet__owner")
    autocomplete_fields = ("pet",)

    @admin.display(description="Хозяин", ordering="pet__owner__name")
    def owner_name(self, record):
        return record.pet.owner.name
