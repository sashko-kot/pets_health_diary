from dataclasses import dataclass


@dataclass(frozen=True)
class Pet:
    id: int
    name: str
    species: str
    owner_id: int
    weight_kg: float
    recommended_weight_kg: float

    @property
    def weight_status(self) -> str:
        return check_weight_status(self.weight_kg, self.recommended_weight_kg)

    @property
    def info(self) -> str:
        weight = format_weight(self.weight_kg)
        return (
            f"{self.name} ({self.species}), вес: {weight}, "
            f"{self.weight_status}"
        )

    def __str__(self) -> str:
        return f"{self.id}: {self.info} [хозяин ID {self.owner_id}]"


def check_weight_status(current_w: float, target_w: float) -> str:
    if current_w > target_w:
        return "Есть избыточный вес, требуется корректировка рациона."
    if current_w < target_w:
        return "Вес ниже нормы."
    return "Вес в норме!"


def format_weight(weight_kg: float) -> str:
    if weight_kg < 1:
        return f"{weight_kg * 1000:.0f} г"
    return f"{weight_kg:.1f} кг"


def add_pet(
    pets: list[Pet],
    name: str,
    species: str,
    owner_id: int,
    weight_kg: float,
    recommended_weight_kg: float,
) -> Pet:
    pet = Pet(
        id=max((item.id for item in pets), default=0) + 1,
        name=name.strip(),
        species=species.strip(),
        owner_id=owner_id,
        weight_kg=weight_kg,
        recommended_weight_kg=recommended_weight_kg,
    )
    pets.append(pet)
    return pet


def find_pet(pets: list[Pet], query: str) -> list[Pet]:
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return []
    return [
        pet
        for pet in pets
        if normalized_query in pet.name.casefold()
        or normalized_query in pet.species.casefold()
    ]


def find_pet_by_id(pets: list[Pet], pet_id: int) -> Pet | None:
    for pet in pets:
        if pet.id == pet_id:
            return pet
    return None


def check_pet_weight(pets: list[Pet], pet_id: int) -> str | None:
    pet = find_pet_by_id(pets, pet_id)
    return pet.weight_status if pet is not None else None


def filter_pets_by_species(pets: list[Pet], species: str) -> list[Pet]:
    normalized_species = species.strip().casefold()
    return [
        pet
        for pet in pets
        if normalized_species in pet.species.casefold()
    ]


def sort_pets(pets: list[Pet], sort_by: str = "name") -> list[Pet]:
    sort_keys = {
        "name": lambda pet: pet.name.casefold(),
        "species": lambda pet: pet.species.casefold(),
        "weight": lambda pet: pet.weight_kg,
    }
    if sort_by not in sort_keys:
        raise ValueError(f"Unsupported pet sort key: {sort_by}")
    return sorted(pets, key=sort_keys[sort_by])


def show_pets(pets: list[Pet]) -> None:
    for pet in pets:
        print(pet)
