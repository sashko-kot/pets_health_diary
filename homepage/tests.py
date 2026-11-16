import hashlib
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from owners.models import Owner as OwnerModel
from pets.models import Pet as PetModel
from records.models import HealthRecord as HealthRecordModel
from models.owners import Owner, add_owner, find_owner
from models.pets import (
    Pet,
    add_pet,
    check_pet_weight,
    filter_pets_by_species,
    find_pet,
    sort_pets,
)
from models.records import (
    HealthRecord,
    add_record,
    find_records_by_pet_id,
    sort_records,
)
from storage import (
    load_owners,
    load_pets,
    load_records,
    save_owners,
    save_pets,
    save_records,
)


class PageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        OwnerModel.objects.bulk_create([
            OwnerModel(id=owner.id, name=owner.name, email=owner.email)
            for owner in load_owners()
        ])
        PetModel.objects.bulk_create([
            PetModel(
                id=pet.id,
                name=pet.name,
                slug=slugify(pet.name, allow_unicode=True),
                species=pet.species,
                owner_id=pet.owner_id,
                weight_kg=pet.weight_kg,
                recommended_weight_kg=pet.recommended_weight_kg,
            )
            for pet in load_pets()
        ])
        HealthRecordModel.objects.bulk_create([
            HealthRecordModel(
                id=record.id,
                pet_id=record.pet_id,
                recorded_on=record.recorded_on,
                activity=record.activity,
                appetite=record.appetite,
                symptoms=record.symptoms,
                weight_kg=record.weight_kg,
            )
            for record in load_records()
        ])

    def test_homepage_is_available(self):
        response = self.client.get(reverse("homepage:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Дневник здоровья грызунов")
        self.assertTemplateUsed(response, "homepage/index.html")
        self.assertContains(response, "/static/homepage/css/style.css")
        self.assertContains(response, "/static/homepage/js/main.js")
        self.assertContains(response, "/static/homepage/img/logo.svg")

    def test_pets_list_is_available(self):
        response = self.client.get(reverse("pets:pets_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pets/pets_list.html")
        self.assertContains(response, "Шуша")
        self.assertContains(response, "Пончик")
        self.assertContains(response, "Шиншилла")
        self.assertContains(response, "Алексей")
        self.assertContains(response, "Мария")

    def test_pet_detail_is_available(self):
        response = self.client.get(reverse("pets:pet_detail", args=[1]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Шуша")
        self.assertContains(response, "Владелец")
        self.assertContains(response, "История здоровья")

    def test_missing_pet_detail_returns_404(self):
        response = self.client.get(reverse("pets:pet_detail", args=[999]))

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Питомец не найден", status_code=404)

    def test_records_list_is_available(self):
        response = self.client.get(reverse("records:records_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_records"], 18)
        self.assertContains(response, "Запись от 12.10.2026")
        self.assertContains(response, "Шуша")
        self.assertContains(response, "Пончик")
        self.assertContains(response, "Рыжик")

    def test_records_list_filters_sorts_and_paginates(self):
        response = self.client.get(
            reverse("records:records_list"),
            {
                "date_from": "2026-10-04",
                "pet": "1",
                "owner": "1",
                "sort": "date",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_records"], 2)
        self.assertContains(response, "Шуша")

        response = self.client.get(
            reverse("records:records_list"),
            {
                "date_from": "2026-10-04",
                "sort": "pet",
                "page": "2",
            },
        )
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertContains(response, "date_from=2026-10-04")
        self.assertContains(response, "sort=pet")
        self.assertContains(response, "page=1")

    def test_records_list_handles_invalid_dates_and_page_numbers(self):
        response = self.client.get(
            reverse("records:records_list"),
            {"date_from": "not-a-date"},
        )
        self.assertEqual(response.context["total_records"], 0)
        self.assertContains(response, "Укажите корректный диапазон дат.")

        response = self.client.get(
            reverse("records:records_list"),
            {"page": "not-a-page"},
        )
        self.assertEqual(response.context["page_obj"].number, 1)

    def test_records_search_combines_symptom_and_date_filters(self):
        response = self.client.get(
            reverse("records:records_search"),
            {
                "symptom": "Нет",
                "date_from": "2026-10-10",
                "date_to": "2026-10-12",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["records"]), 8)

    def test_statistics_page_uses_orm_aggregates(self):
        response = self.client.get(reverse("records:statistics"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["pet_statistics"]), 9)
        self.assertEqual(
            response.context["pet_statistics"][0]["records_count"],
            2,
        )
        self.assertEqual(
            response.context["owner_statistics"][0]["pets_count"],
            1,
        )
        self.assertContains(response, "Часто встречающиеся симптомы")
        self.assertContains(
            response,
            "Сводная таблица: хозяева, питомцы и записи",
        )
        self.assertEqual(len(response.context["record_summary"]), 18)
        first_record = response.context["record_summary"][0]
        related_record = HealthRecordModel.objects.get(pk=first_record["id"])
        self.assertEqual(
            first_record["owner_name"],
            related_record.pet.owner.name,
        )
        self.assertEqual(
            first_record["owner_email"],
            related_record.pet.owner.email,
        )
        self.assertTrue(first_record["pet_slug"])

    def test_pet_slug_url_and_record_queryset_methods(self):
        pet = PetModel.objects.get(pk=1)
        self.assertEqual(pet.get_absolute_url(), reverse(
            "pets:pet_detail_by_slug",
            kwargs={"slug": pet.slug},
        ))
        self.assertEqual(
            self.client.get(pet.get_absolute_url()).status_code,
            200,
        )

        owner = OwnerModel.objects.get(pk=pet.owner_id)
        recorded_on = date(2026, 10, 12)
        records = HealthRecordModel.objects.for_owner(owner).for_date(
            recorded_on
        )
        self.assertTrue(records.exists())
        self.assertTrue(all(item.pet.owner_id == owner.pk for item in records))

    def test_admin_inlines_show_related_pets_and_health_records(self):
        admin_user = get_user_model().objects.create_superuser(
            username="practice-admin",
            email="admin@example.test",
            password="test-password",
        )
        self.client.force_login(admin_user)

        owner_response = self.client.get(
            reverse("admin:owners_owner_change", args=[1])
        )
        self.assertEqual(owner_response.status_code, 200)
        self.assertContains(owner_response, "Шуша")

        pet_response = self.client.get(
            reverse("admin:pets_pet_change", args=[1])
        )
        self.assertEqual(pet_response.status_code, 200)
        self.assertContains(pet_response, "health_records")
        self.assertContains(pet_response, "Дата наблюдения")

        record_response = self.client.get(
            reverse("admin:records_healthrecord_changelist")
        )
        self.assertEqual(record_response.status_code, 200)
        search_response = self.client.get(
            reverse("admin:records_healthrecord_changelist"),
            {"q": OwnerModel.objects.get(pk=1).name},
        )
        self.assertEqual(search_response.status_code, 200)
        self.assertGreater(search_response.context["cl"].result_count, 0)

    def test_duplicate_pet_names_receive_unique_slugs(self):
        owner = OwnerModel.objects.get(pk=1)
        pet_fields = {
            "name": "Проверка slug",
            "species": "Хомяк",
            "owner": owner,
            "weight_kg": 0.1,
            "recommended_weight_kg": 0.12,
        }
        first_pet = PetModel.objects.create(**pet_fields)
        second_pet = PetModel.objects.create(**pet_fields)

        self.assertNotEqual(first_pet.slug, second_pet.slug)
        self.assertEqual(second_pet.slug, f"{first_pet.slug}-2")

    def test_json_data_has_rodents_and_records_for_every_pet(self):
        pets = load_pets()
        records = load_records()
        pet_ids = {pet.id for pet in pets}

        owners = load_owners()
        owner_ids = {owner.id for owner in owners}

        self.assertEqual(len(pets), 9)
        self.assertEqual(len(records), 18)
        self.assertTrue(all(pet.owner_id in owner_ids for pet in pets))
        self.assertTrue(all(record.pet_id in pet_ids for record in records))

    def test_owners_with_same_name_have_distinct_ids(self):
        marias = [owner for owner in load_owners() if owner.name == "Мария"]

        self.assertEqual(len(marias), 2)
        self.assertNotEqual(marias[0].id, marias[1].id)
        self.assertEqual(len(find_owner(load_owners(), "maria.first")), 1)

    def test_entity_operations_use_their_collections(self):
        owners = [Owner(1, "Мария", "maria@example.test")]
        owner = add_owner(owners, "Иван", " IVAN@example.test ")
        self.assertEqual(owner.id, 2)
        self.assertEqual(owner.email, "ivan@example.test")

        pets = [
            Pet(1, "Шуша", "Морская свинка", 1, 0.85, 0.9),
            Pet(2, "Пончик", "Хомяк", 2, 0.14, 0.15),
        ]
        pet = add_pet(pets, "Ириска", "Хомяк", 2, 0.035, 0.03)
        self.assertEqual(pet.id, 3)
        self.assertEqual([item.id for item in find_pet(pets, "хом")], [2, 3])
        filtered = filter_pets_by_species(pets, "свинка")
        self.assertEqual([item.id for item in filtered], [1])
        self.assertEqual([item.id for item in sort_pets(pets)], [3, 2, 1])
        self.assertEqual(check_pet_weight(pets, 3), pet.weight_status)
        self.assertIsNone(check_pet_weight(pets, 999))

        records = [
            HealthRecord(
                1,
                1,
                date(2026, 10, 1),
                "Обычная",
                "Хороший",
                "Нет",
                0.84,
            )
        ]
        record = add_record(
            records,
            1,
            date(2026, 10, 12),
            "Активная",
            "Хороший",
            "Нет",
            0.85,
        )
        self.assertEqual(record.id, 2)
        self.assertEqual(find_records_by_pet_id(records, 1), records)
        self.assertEqual(sort_records(records)[0].id, 2)

    def test_entity_storage_round_trip(self):
        owners = [Owner(1, "Алексей", "alexey@example.test")]
        pets = [Pet(1, "Шуша", "Морская свинка", 1, 0.85, 0.9)]
        records = [
            HealthRecord(
                1,
                1,
                date(2026, 10, 12),
                "Активная",
                "Хороший",
                "Нет",
                0.85,
            )
        ]

        with TemporaryDirectory() as directory:
            with patch("storage.DATA_DIR", Path(directory)):
                save_owners(owners)
                save_pets(pets)
                save_records(records)

                self.assertEqual(load_owners(), owners)
                self.assertEqual(load_pets(), pets)
                self.assertEqual(load_records(), records)

    def test_pet_detail_shows_owner_id(self):
        response = self.client.get(reverse("pets:pet_detail", args=[9]))

        self.assertContains(response, "Мария")
        self.assertContains(response, "(ID 9)")

    def test_pet_weights_are_displayed_in_grams(self):
        response = self.client.get(reverse("pets:pet_detail", args=[3]))

        self.assertContains(response, "35 г")

    def test_record_detail_is_available(self):
        response = self.client.get(reverse("records:record_detail", args=[1]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Осмотр питомца Шуша")

    def test_missing_record_detail_returns_404(self):
        detail_url = reverse("records:record_detail", args=[999])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Запись не найдена", status_code=404)

    def test_empty_pet_list_uses_empty_template_branch(self):
        response = self.client.get(
            reverse("pets:pets_list"),
            {"species": "несуществующий вид"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Питомцев пока нет.")

    def test_orm_models_support_related_crud_operations(self):
        owner = OwnerModel.objects.create(
            name="Тестовый хозяин",
            email="orm-test@example.test",
        )
        pet = PetModel.objects.create(
            name="Тестовый питомец",
            species="Хомяк",
            owner=owner,
            weight_kg=0.1,
            recommended_weight_kg=0.12,
        )
        record = HealthRecordModel.objects.create(
            pet=pet,
            recorded_on=date(2026, 10, 13),
            activity="Активная",
            appetite="Хороший",
            symptoms="Нет",
            weight_kg=0.1,
        )

        self.assertEqual(record.pet.owner, owner)
        self.assertEqual(owner.pets.get(), pet)
        record.appetite = "Сниженный"
        record.save(update_fields=["appetite"])
        self.assertEqual(
            HealthRecordModel.objects.get(pk=record.pk).appetite,
            "Сниженный",
        )
        record.delete()
        self.assertFalse(
            HealthRecordModel.objects.filter(pk=record.pk).exists()
        )

    def test_legacy_database_import_is_repeatable(self):
        from db.import_sqlite_to_orm import SOURCE_DB, import_sqlite_to_orm

        source_hash = hashlib.sha256(SOURCE_DB.read_bytes()).digest()
        first_counts = import_sqlite_to_orm()
        second_counts = import_sqlite_to_orm()

        self.assertEqual(first_counts, {
            "owners": 9,
            "pets": 9,
            "health_records": 18,
        })
        self.assertEqual(second_counts, first_counts)
        self.assertEqual(
            hashlib.sha256(SOURCE_DB.read_bytes()).digest(),
            source_hash,
        )

    def test_not_found_page_uses_custom_handler(self):
        with self.settings(DEBUG=False, ALLOWED_HOSTS=["testserver"]):
            response = self.client.get("/missing-page/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Страница не найдена", status_code=404)
