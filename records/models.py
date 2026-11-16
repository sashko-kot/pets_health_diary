from django.db import models

from pets.models import Pet


class HealthRecord(models.Model):
    id = models.IntegerField(primary_key=True)
    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT,
        related_name="health_records",
        db_column="pet_id",
    )
    recorded_on = models.DateField()
    activity = models.CharField(max_length=255)
    appetite = models.CharField(max_length=255)
    symptoms = models.CharField(max_length=255)
    weight_kg = models.FloatField()

    class Meta:
        managed = False
        db_table = "health_records"

    def __str__(self) -> str:
        return f"{self.recorded_on} — {self.pet}"
