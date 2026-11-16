from django.db import models

from owners.models import Owner


class Pet(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    owner = models.ForeignKey(
        Owner,
        on_delete=models.PROTECT,
        related_name="pets",
        db_column="owner_id",
    )
    weight_kg = models.FloatField()
    recommended_weight_kg = models.FloatField()

    class Meta:
        managed = False
        db_table = "pets"

    def __str__(self) -> str:
        return self.name
