# Дневник здоровья питомцев

Учебный проект для учёта хозяев, питомцев и наблюдений за их здоровьем.
Веб-приложение работает с предметными данными через Django ORM и SQLite.
Исходная SQLite-база и JSON-файлы сохранены для переноса данных и прежней
консольной версии.

## Структура данных

- `owners` — хозяева: имя и электронная почта;
- `pets` — питомцы: вид, вес, рекомендуемый вес и внешний ключ `owner_id`;
- `health_records` — наблюдения: дата, активность, аппетит, симптомы, вес и
  внешний ключ `pet_id`.

Модели Django расположены в приложениях `owners`, `pets` и `records`.
Связи «один ко многим» заданы внешними ключами: у хозяина может быть несколько
питомцев, у питомца — несколько записей о здоровье. Удаление связанных
объектов защищено от потери истории. Веб-представления используют ORM;
таблицы целевой базы `db.sqlite3` создаются миграциями.

Файл `data/pets_health.sqlite` — исходная база предыдущей версии проекта.
Скрипт `db/import_sqlite_to_orm.py` переносит из неё данные в базу Django,
сохраняя идентификаторы и связи. Он читает исходную базу и безопасен для
повторного запуска. JSON-файлы, `db/import_json.py`, `db/database.py` и
SQL-файлы сохранены для консольной версии и прежней схемы.

## Страницы

- `/` — главная и количество питомцев и записей;
- `/pets/` и `/pets/<id>/` — список и карточка питомца с историей здоровья;
- `/pets/<slug>/` — карточка питомца по именованному slug-маршруту;
- `/records/` и `/records/<id>/` — фильтруемый, сортируемый и постраничный
  список записей, а также карточка записи;
- `/records/search/` — поиск записей по симптомам;
- `/records/statistics/` — сводная таблица хозяев, питомцев и записей, число
  записей и средний вес по питомцам, статистика симптомов.

Страницы используют Django ORM и базу `db.sqlite3`. Поиск и фильтры
поддерживают одновременное применение условий; сортировка ограничена
разрешёнными полями, а пагинация сохраняет параметры запроса. JSON остаётся
доступен консольной версии.

## Django Admin и связи

Создайте администратора командой `python manage.py createsuperuser` и откройте
`/admin/`. В списках хозяев, питомцев и записей настроены столбцы, поиск,
фильтры и сортировка. В карточке хозяина питомцы доступны через inline, а в
карточке питомца — связанные записи здоровья. Связи защищены через
`on_delete=PROTECT`, чтобы нельзя было случайно удалить хозяина или питомца,
если от него зависят данные.

Страница `/records/statistics/` содержит построчную сводку: дата записи,
хозяин и его почта, питомец и его вид, активность, аппетит, симптомы и вес.
Связанные значения выбираются одним ORM-запросом через
`HealthRecord.objects.summary()`.

## Демонстрация ORM

В Django Shell можно проверить связи и QuerySet-методы:

```python
from datetime import date
from pets.models import Pet
from records.models import HealthRecord

HealthRecord.objects.for_date(date(2026, 10, 12))
HealthRecord.objects.filter(pet__owner__name__icontains="Алексей")
HealthRecord.objects.filter(pet__name__icontains="Шуша").values(
    "recorded_on", "pet__name", "pet__owner__name", "weight_kg"
)
list(HealthRecord.objects.summary()[:5])
Pet.objects.select_related("owner").prefetch_related("health_records")
```

Для безопасной демонстрации создания и удаления используйте только запись,
созданную в той же сессии Shell:

```python
pet = Pet.objects.first()
test_record = HealthRecord.objects.create(
    pet=pet,
    recorded_on=date.today(),
    activity="Тестовая запись",
    appetite="Не указано",
    symptoms="",
    weight_kg=pet.weight_kg,
)
test_record.appetite = "Хороший"
test_record.save(update_fields=["appetite"])
test_record.delete()
```

Изменение `Pet.slug` демонстрируется миграцией `pets/0002_pet_slug.py`:
сначала добавляется временно допускающее `NULL` поле, затем существующие
питомцы получают уникальные slug, после чего поле становится уникальным;
новым питомцам slug присваивается при сохранении. Для кириллических slug
маршрут использует конвертер `unicode_slug`. `makemigrations` создаёт файл
описания схемы, а `migrate` применяет
операции и изменение данных к базе. В этой предметной области нет полей
`is_cancelled` или статусов бронирования: медицинским записям такие состояния
не соответствуют, поэтому миграцию отмен/завершений не имитируем.

## Установка и запуск

Из корня проекта в PowerShell:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m db.import_sqlite_to_orm
.\venv\Scripts\python.exe manage.py runserver
```

Сервер доступен по адресу `http://127.0.0.1:8000/`. Перенос сохраняет
исходный файл `data/pets_health.sqlite` и обновляет записи в базе Django по
их идентификаторам.

## Доступ к данным

Запросы списков, карточек, поиска и статистики выполняются средствами Django
ORM, включая фильтрацию связанных моделей, агрегаты и подсчёты. Старые
SQL-запросы в `sql/queries.sql` оставлены для прежней SQLite-схемы.

## Проверки

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe -m pytest -v
.\venv\Scripts\python.exe -m flake8 . --extend-exclude=venv
```

## Основные файлы

```text
owners/models.py       модель хозяина
pets/models.py         модель питомца
records/models.py      модель записи о здоровье
db/import_sqlite_to_orm.py перенос данных в базу Django
data/pets_health.sqlite исходная база предыдущей версии
data/*.json            исходные данные консольной версии
db.sqlite3             база веб-приложения, создаваемая миграциями
```
