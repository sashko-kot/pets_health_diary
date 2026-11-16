from django.db import models


class Owner(models.Model):
    name = models.CharField(max_length=200, verbose_name="Имя хозяина")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Хозяин"
        verbose_name_plural = "Хозяева"
