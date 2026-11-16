from django.contrib import admin

from .models import Pet
from records.models import HealthRecord


class HealthRecordInline(admin.TabularInline):
    model = HealthRecord
    extra = 0
    show_change_link = True
    fields = (
        "recorded_on",
        "activity",
        "appetite",
        "symptoms",
        "weight_kg",
    )
    ordering = ("-recorded_on", "-pk")


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "species", "owner", "weight_kg", "weight_status")
    list_filter = ("species", "owner")
    search_fields = ("name", "species", "owner__name", "owner__email")
    ordering = ("name", "pk")
    list_select_related = ("owner",)
    readonly_fields = ("slug",)
    inlines = (HealthRecordInline,)

    @admin.display(description="Оценка веса")
    def weight_status(self, pet):
        return pet.weight_status
