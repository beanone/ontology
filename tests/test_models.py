"""Test cases for data models."""

import pytest
from marshmallow import ValidationError

from ontology.models import Entity, Relation


def test_entity_creation() -> None:
    """Test basic Entity creation."""
    entity = Entity(name="test", entity_type="project", observations=["test observation"])
    assert entity.name == "test"
    assert entity.entity_type == "project"
    assert entity.observations == ["test observation"]


def test_entity_from_dict() -> None:
    """Test Entity creation from dictionary."""
    data = {
        "name": "test",
        "entity_type": "project",
        "observations": ["test observation"]
    }
    entity = Entity.from_dict(data)

    assert isinstance(entity, Entity)
    assert entity.name == "test"
    assert entity.entity_type == "project"
    assert entity.observations == ["test observation"]


def test_entity_to_dict() -> None:
    """Test Entity serialization to dictionary."""
    entity = Entity(name="test", entity_type="project", observations=["test observation"])
    result = entity.to_dict()

    assert result["name"] == "test"
    assert result["entity_type"] == "project"
    assert result["observations"] == ["test observation"]


def test_entity_missing_observations() -> None:
    """Test Entity creation with missing observations defaults to empty list."""
    data = {
        "name": "test",
        "entity_type": "project"
    }
    entity = Entity.from_dict(data)

    assert isinstance(entity, Entity)
    assert entity.observations == []


def test_entity_validation_error() -> None:
    """Test Entity validation errors."""
    invalid_data = {
        "entity_type": "project",  # Missing required 'name' field
        "observations": []
    }

    with pytest.raises(ValidationError) as exc_info:
        Entity.from_dict(invalid_data)

    assert "name" in str(exc_info.value)


def test_relation_creation() -> None:
    """Test basic Relation creation."""
    relation = Relation(
        from_entity="entity1",
        to_entity="entity2",
        relation_type="has_component"
    )
    assert relation.from_entity == "entity1"
    assert relation.to_entity == "entity2"
    assert relation.relation_type == "has_component"


def test_relation_from_dict() -> None:
    """Test Relation creation from dictionary."""
    data = {
        "from_entity": "entity1",
        "to_entity": "entity2",
        "relation_type": "has_component"
    }
    relation = Relation.from_dict(data)

    assert isinstance(relation, Relation)
    assert relation.from_entity == "entity1"
    assert relation.to_entity == "entity2"
    assert relation.relation_type == "has_component"


def test_relation_to_dict() -> None:
    """Test Relation serialization to dictionary."""
    relation = Relation(
        from_entity="entity1",
        to_entity="entity2",
        relation_type="has_component"
    )
    result = relation.to_dict()

    assert result["from_entity"] == "entity1"
    assert result["to_entity"] == "entity2"
    assert result["relation_type"] == "has_component"


def test_relation_validation_error() -> None:
    """Test Relation validation errors."""
    invalid_data = {
        "from_entity": "entity1",
        # Missing required 'to_entity' field
        "relation_type": "has_component"
    }

    with pytest.raises(ValidationError) as exc_info:
        Relation.from_dict(invalid_data)

    assert "to_entity" in str(exc_info.value)


def test_entity_empty_observations() -> None:
    """Test Entity with empty observations list."""
    data = {
        "name": "test",
        "entity_type": "project",
        "observations": []
    }
    entity = Entity.from_dict(data)

    assert isinstance(entity, Entity)
    assert entity.observations == []


def test_entity_invalid_observations() -> None:
    """Test Entity with invalid observations type."""
    invalid_data = {
        "name": "test",
        "entity_type": "project",
        "observations": "not a list"  # Should be a list
    }

    with pytest.raises(ValidationError) as exc_info:
        Entity.from_dict(invalid_data)

    assert "observations" in str(exc_info.value)


def test_relation_empty_fields() -> None:
    """Test Relation with empty string fields."""
    invalid_data = {
        "from_entity": "",
        "to_entity": "entity2",
        "relation_type": "has_component"
    }

    with pytest.raises(ValidationError) as exc_info:
        Relation.from_dict(invalid_data)

    assert "from_entity" in str(exc_info.value)