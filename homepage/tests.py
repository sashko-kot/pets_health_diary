from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

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
        self.assertContains(response, "Запись от 12.10.2026")
        self.assertContains(response, "Шуша")
        self.assertContains(response, "Пончик")
        self.assertContains(response, "Рыжик")

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
        with (
            patch(
                "pets.views.load_queries",
                return_value={"list_pets": "SELECT 1"},
            ),
            patch("pets.views.get_connection") as get_connection,
        ):
            get_connection.return_value.__enter__.return_value.execute.\
                return_value.fetchall.return_value = []
            response = self.client.get(reverse("pets:pets_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Питомцев пока нет.")

    def test_not_found_page_uses_custom_handler(self):
        with self.settings(DEBUG=False, ALLOWED_HOSTS=["testserver"]):
            response = self.client.get("/missing-page/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Страница не найдена", status_code=404)
