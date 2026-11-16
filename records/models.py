from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from pets.models import Pet


class HealthRecordQuerySet(models.QuerySet):
    def for_date(self, recorded_on):
        return self.filter(recorded_on=recorded_on)

    def for_pet(self, pet):
        return self.filter(pet=pet)

    def for_owner(self, owner):
        return self.filter(pet__owner=owner)

    def summary(self):
        return (
            self.annotate(
                pet_name=models.F("pet__name"),
                pet_slug=models.F("pet__slug"),
                pet_species=models.F("pet__species"),
                owner_name=models.F("pet__owner__name"),
                owner_email=models.F("pet__owner__email"),
            )
            .values(
                "id",
                "recorded_on",
                "activity",
                "appetite",
                "symptoms",
                "weight_kg",
                "pet_name",
                "pet_slug",
                "pet_species",
                "owner_name",
                "owner_email",
            )
            .order_by("-recorded_on", "-pk")
        )


class HealthRecord(models.Model):
    objects = HealthRecordQuerySet.as_manager()

    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT,
        related_name="health_records",
        verbose_name="Питомец",
    )
    recorded_on = models.DateField(verbose_name="Дата наблюдения")
    activity = models.CharField(max_length=200, verbose_name="Активность")
    appetite = models.CharField(max_length=200, verbose_name="Аппетит")
    symptoms = models.TextField(
        blank=True,
        default="",
        verbose_name="Симптомы",
    )
    weight_kg = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Вес, кг",
    )

    def __str__(self) -> str:
        return f"{self.pet} — {self.recorded_on:%d.%m.%Y}"

    class Meta:
        ordering = ["-recorded_on", "-pk"]
        verbose_name = "Запись о здоровье"
        verbose_name_plural = "Записи о здоровье"
        constraints = [
            models.CheckConstraint(
                condition=Q(weight_kg__gte=0),
                name="health_records_weight_nonnegative",
            ),
        ]
