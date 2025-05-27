from typing import Any, Optional, TypeVar, cast

from sqlalchemy.orm import Mapped, mapped_column

from .entity import Entity, EntityType

T = TypeVar("T", bound="ConcreteEntity")


class ConcreteEntity(Entity):
    """Concrete implementation of the Entity model for database storage."""

    __tablename__ = "entities"

    # Override the abstract columns to make them concrete
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    entity_type: Mapped[EntityType] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    metadata_: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata", nullable=True
    )
    created_at = Entity.created_at
    updated_at = Entity.updated_at

    def __init__(
        self,
        name: str,
        entity_type: EntityType,
        description: Optional[str] = None,
        metadata_: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name=name,
            entity_type=entity_type,
            description=description,
            metadata_=metadata_,
        )

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Create a ConcreteEntity instance from a dictionary."""
        return cast(T, super().from_dict(data))
