from django.db import migrations, models
from django.utils.text import slugify


def populate_pet_slugs(apps, schema_editor):
    Pet = apps.get_model("pets", "Pet")
    database = schema_editor.connection.alias

    for pet in Pet.objects.using(database).order_by("pk").iterator():
        base_slug = slugify(pet.name, allow_unicode=True) or f"pet-{pet.pk}"
        slug = base_slug
        suffix = 2
        while (
            Pet.objects.using(database)
            .filter(slug=slug)
            .exclude(pk=pet.pk)
            .exists()
        ):
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        Pet.objects.using(database).filter(pk=pet.pk).update(slug=slug)


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pet",
            name="slug",
            field=models.SlugField(max_length=220, null=True),
        ),
        migrations.RunPython(
            populate_pet_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="pet",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, unique=True),
        ),
    ]
