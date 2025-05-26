from __future__ import annotations

from datetime import datetime
from enum import Enum as PythonEnum
from typing import Any, Dict, Optional, Type, TypeVar, cast, final

from sqlalchemy import Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func as sql_func

from base import Base

# Type variable for entity subclasses
T = TypeVar("T", bound="Entity")


class EntityType(str, PythonEnum):
    """Enum representing the types of entities in the system."""

    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    EVENT = "EVENT"
    WORK_OF_ART = "WORK_OF_ART"
    CONSUMER_GOOD = "CONSUMER_GOOD"
    OTHER = "OTHER"


@final  # Mark as final to indicate it shouldn't be subclassed directly
class Entity(Base):
    """Base class for all entity types in the system."""

    __abstract__: bool = True

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, name="entity_type"), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(  # type: ignore[assignment]
        "metadata", JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=sql_func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=sql_func.now(), onupdate=sql_func.now()
    )

    def __init__(
        self,
        name: str,
        entity_type: EntityType,
        description: Optional[str] = None,
        metadata_: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a new Entity.

        Args:
            name: The name of the entity
            entity_type: The type of the entity
            description: Optional description of the entity
            metadata_: Optional metadata for the entity
        """
        super().__init__()
        self.name = name
        self.entity_type = entity_type
        self.description = description
        self.metadata_ = metadata_

    def __repr__(self) -> str:
        """Return a string representation of the entity.

        Returns:
            str: A string representation of the entity
        """
        return f"<{self.__class__.__name__}(id={self.id}, name='{self.name}', type='{self.entity_type}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the entity
        """
        result = super().to_dict()
        # Ensure entity_type is properly serialized
        if "entity_type" in result and hasattr(result["entity_type"], "value"):
            result["entity_type"] = result["entity_type"].value
        return result

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an Entity instance from a dictionary.

        Args:
            data: Dictionary containing entity data

        Returns:
            T: A new instance of the entity

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if "entity_type" not in data:
            raise ValueError("entity_type is required")

        try:
            entity_type = EntityType(cast(str, data["entity_type"]))
        except ValueError as e:
            raise ValueError(f"Invalid entity_type: {data['entity_type']}") from e

        if "name" not in data:
            raise ValueError("name is required")

        return cls(
            name=cast(str, data["name"]),
            entity_type=entity_type,
            description=cast(Optional[str], data.get("description")),
            metadata_=cast(Optional[Dict[str, Any]], data.get("metadata")),
        )
