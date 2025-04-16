"""Data models for the knowledge graph with Marshmallow schemas."""

from dataclasses import dataclass
from typing import Any, ClassVar

from marshmallow import Schema, ValidationError, fields, post_load, validate


@dataclass
class Entity:
    """Represents an entity in the knowledge graph.

    Attributes:
        name: Unique identifier for the entity
        entity_type: Type classification of the entity
        observations: List of observations about the entity
    """

    name: str
    entity_type: str
    observations: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Entity":
        """Create an Entity from a dictionary with validation.

        Args:
            data: Dictionary containing entity data

        Returns:
            Entity instance

        Raises:
            ValidationError: If the data is invalid
        """
        return _entity_schema.load(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert Entity to a dictionary.

        Returns:
            Dictionary representation of the entity
        """
        return _entity_schema.dump(self)


class EntitySchema(Schema):
    """Schema for Entity validation and serialization."""
    name = fields.Str(required=True, validate=validate.Length(min=1))
    entity_type = fields.Str(required=True, validate=validate.Length(min=1))
    observations = fields.List(fields.Str(), load_default=list)

    @post_load
    def make_entity(self, data, **kwargs) -> Entity:
        return Entity(**data)


@dataclass
class Relation:
    """Represents a relation between entities in the knowledge graph.

    Attributes:
        from_entity: Source entity name
        to_entity: Target entity name
        relation_type: Type of relationship
    """

    from_entity: str
    to_entity: str
    relation_type: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relation":
        """Create a Relation from a dictionary with validation.

        Args:
            data: Dictionary containing relation data

        Returns:
            Relation instance

        Raises:
            ValidationError: If the data is invalid
        """
        return _relation_schema.load(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert Relation to a dictionary.

        Returns:
            Dictionary representation of the relation
        """
        return _relation_schema.dump(self)


class RelationSchema(Schema):
    """Schema for Relation validation and serialization."""
    from_entity = fields.Str(required=True, validate=validate.Length(min=1))
    to_entity = fields.Str(required=True, validate=validate.Length(min=1))
    relation_type = fields.Str(required=True, validate=validate.Length(min=1))

    @post_load
    def make_relation(self, data, **kwargs) -> Relation:
        return Relation(**data)


# Create private schema instances
_entity_schema = EntitySchema()
_relation_schema = RelationSchema()

# Re-export ValidationError for convenience
__all__ = ["Entity", "Relation", "ValidationError"]
