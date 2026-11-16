from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify

from models.pets import check_weight_status
from owners.models import Owner


class Pet(models.Model):
    name = models.CharField(max_length=200, verbose_name="Имя питомца")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    species = models.CharField(max_length=200, verbose_name="Вид")
    owner = models.ForeignKey(
        Owner,
        on_delete=models.PROTECT,
        related_name="pets",
        verbose_name="Хозяин",
    )
    weight_kg = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Текущий вес, кг",
    )
    recommended_weight_kg = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Рекомендуемый вес, кг",
    )

    @property
    def weight_status(self) -> str:
        return check_weight_status(
            self.weight_kg,
            self.recommended_weight_kg,
        )

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or "pet"
            self.slug = base_slug
            suffix = 2
            while (
                type(self).objects.filter(slug=self.slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                self.slug = f"{base_slug}-{suffix}"
                suffix += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("pets:pet_detail_by_slug", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Питомец"
        verbose_name_plural = "Питомцы"
        constraints = [
            models.CheckConstraint(
                condition=Q(weight_kg__gte=0),
                name="pets_weight_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(recommended_weight_kg__gte=0),
                name="pets_recommended_weight_nonnegative",
            ),
        ]
