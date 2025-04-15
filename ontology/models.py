"""Data models for the knowledge graph.

This module provides the dataclasses for representing entities and relations
in the knowledge graph.
"""

from dataclasses import dataclass


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
