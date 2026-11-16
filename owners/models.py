from django.db import models


class Owner(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    class Meta:
        managed = False
        db_table = "owners"

    def __str__(self) -> str:
        return self.name
