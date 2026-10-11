from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Owner:
    id: int
    name: str
    email: str

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "Owner":
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            email=str(data["email"]),
        )

    def __str__(self) -> str:
        return f"{self.id}: {self.name} ({self.email})"


def add_owner(owners: list[Owner], name: str, email: str) -> Owner:
    owner = Owner(
        id=max((item.id for item in owners), default=0) + 1,
        name=name.strip(),
        email=email.strip().casefold(),
    )
    owners.append(owner)
    return owner


def find_owner(owners: list[Owner], query: str) -> list[Owner]:
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return []
    return [
        owner
        for owner in owners
        if normalized_query in owner.name.casefold()
        or normalized_query in owner.email.casefold()
    ]


def find_owner_by_id(owners: list[Owner], owner_id: int) -> Owner | None:
    for owner in owners:
        if owner.id == owner_id:
            return owner
    return None


def show_owners(owners: list[Owner]) -> None:
    for owner in owners:
        print(owner)
