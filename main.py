from datetime import date

from models.owners import find_owner_by_id, show_owners
from models.pets import format_weight, show_pets
from models.records import show_records, sort_records
from storage import load_owners, load_pets, load_records


def calculate_daily_feed(weight: float, rate: float) -> float:
    return weight * rate


def check_cleaning_status(
    last_date: date,
    interval: int,
    today: date,
) -> str:
    days_passed = (today - last_date).days
    if days_passed >= interval:
        return "Пора провести уборку!"
    days_remaining = interval - days_passed
    return f"Уборка не требуется. Дней до следующей уборки: {days_remaining}"


def main() -> None:
    owners = load_owners()
    pets = load_pets()
    records = load_records()

    print("Хозяева:")
    show_owners(owners)

    print("\nПитомцы:")
    show_pets(pets)

    print("\nЗаписи дневника:")
    show_records(sort_records(records))

    if pets:
        pet = pets[0]
        owner = find_owner_by_id(owners, pet.owner_id)
        if owner is None:
            raise ValueError(
                f"Pet {pet.id} refers to missing owner {pet.owner_id}"
            )
        daily_feed = calculate_daily_feed(pet.weight_kg, 20)
        print(f"\nПитомец: {pet.name}; хозяин: {owner.name}")
        print(
            "Суточная норма корма по расчёту проекта: "
            f"{daily_feed:.1f} г."
        )
        print(f"Текущий вес: {format_weight(pet.weight_kg)}.")

    print(
        "\nСтатус уборки клетки: "
        f"{check_cleaning_status(date(2026, 9, 9), 5, date.today())}"
    )


if __name__ == "__main__":
    main()
