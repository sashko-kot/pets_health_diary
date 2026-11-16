from django.contrib import admin
from django.db.models import Count

from .models import Owner
from pets.models import Pet


class PetInline(admin.TabularInline):
    model = Pet
    extra = 0
    show_change_link = True
    fields = (
        "name",
        "species",
        "weight_kg",
        "recommended_weight_kg",
    )


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "pet_count")
    search_fields = ("name", "email")
    ordering = ("name", "pk")
    inlines = (PetInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_pet_count=Count("pets"))

    @admin.display(description="Питомцев", ordering="_pet_count")
    def pet_count(self, owner):
        return owner._pet_count
