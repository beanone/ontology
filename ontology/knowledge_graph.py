"""Knowledge graph implementation.

This module provides a flexible knowledge graph implementation for storing
and retrieving information about entities and their relationships.
"""

import json
import logging
import os
from pathlib import Path

from ontology.models import Entity, Relation

logger = logging.getLogger(__name__)

# Default settings
DEFAULT_MEMORY_FILE_NAME = "memory.json"
DEFAULT_LOCAL_STORAGE = False
DEFAULT_MEMORY_FILE_PATH = "."

# Get settings from environment with defaults
LOCAL_STORAGE = os.getenv("LOCAL_STORAGE", str(DEFAULT_LOCAL_STORAGE)).lower() == "true"


class MemoryError(Exception):
    """Raised when there is an error performing a memory operation."""

    pass


class KnowledgeGraph:
    """Manages the knowledge graph data structure and persistence."""

    def __init__(self) -> None:
        """Initialize the knowledge graph.

        Args:
            memory_file_name: Name of the file to store the graph in.
            local_storage: Whether to use local storage.
            memory_file_path: Path to store the memory file if not using local storage.
        """
        self.memory_file_name = os.getenv("MEMORY_FILE_NAME", DEFAULT_MEMORY_FILE_NAME)
        self.local_storage = os.getenv("LOCAL_STORAGE", str(DEFAULT_LOCAL_STORAGE)).lower() == "true"
        # Use the environment variable if set, otherwise use the provided parameter
        self.memory_file_path = os.getenv("MEMORY_FILE_PATH", DEFAULT_MEMORY_FILE_PATH)

        # Determine storage path
        if self.local_storage:
            self.storage_path = Path.cwd() / self.memory_file_name
        else:
            # Use self.memory_file_path which prioritizes the environment variable
            self.storage_path = Path(self.memory_file_path) / self.memory_file_name

        logger.debug(
            "Knowledge graph initialized with storage path: %s (local_storage=%s)",
            self.storage_path,
            self.local_storage,
        )

        self.entities: dict[str, Entity] = {}
        self.relations: list[Relation] = []
        self._load_graph()

    def clear(self) -> None:
        """Clear the graph state."""
        self.entities = {}
        self.relations = []

    def _load_graph(self) -> None:
        """Load the knowledge graph from storage."""
        # Clear existing state before loading
        self.entities = {}
        self.relations = []

        try:
            if not self.storage_path.exists():
                # Create parent directory if it doesn't exist
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
                # Create empty graph file
                with open(self.storage_path, "w") as f:
                    f.write("")
                    f.flush()
                    os.fsync(f.fileno())
                return

            # Read the file line by line
            with open(self.storage_path) as f:
                content = f.read().strip()
                if not content:  # Empty file
                    return
                self.initialize_graph_from_data(content)
        except (json.JSONDecodeError, OSError) as e:
            # If file is corrupted or there's an IO error, start fresh
            logger.error("Error loading graph: %s", str(e))
            raise

    def initialize_graph_from_data(self, content: str) -> None:
        """Initialize the graph from a string of JSON lines.

        Args:
            content: String containing JSON lines.
        """
        for line in content.split("\n"):
            line_txt = line.strip()
            if not line_txt:
                continue
            try:
                data = json.loads(line_txt)
                if "name" in data:
                    # Entity - ensure observations exists with default empty list
                    if "observations" not in data:
                        data["observations"] = []

                    self.entities[data["name"]] = Entity(
                        name=data["name"],
                        entity_type=data["entity_type"],
                        observations=data["observations"],
                    )
                elif "from_entity" in data:
                    # Relation
                    self.relations.append(
                        Relation(
                            from_entity=data["from_entity"],
                            to_entity=data["to_entity"],
                            relation_type=data["relation_type"],
                        )
                    )
            except json.JSONDecodeError:
                # Log warning for invalid JSON
                logger.warning("Invalid JSON line encountered. Skipping line: %s", line[:100])
                continue
            except KeyError as e:
                # Log warning for missing required fields
                logger.warning("Missing required field in data: %s. Error: %s", line[:100], str(e))
                continue

    def _save_graph(self) -> None:
        """Save the knowledge graph to storage."""
        # Create parent directory if it doesn't exist
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(self.storage_path, "w") as f:
            # Write entities
            for entity in self.entities.values():
                json.dump(
                    {
                        "name": entity.name,
                        "entity_type": entity.entity_type,
                        "observations": entity.observations,
                    },
                    f,
                )
                f.write("\n")

            # Write relations
            for relation in self.relations:
                json.dump(
                    {
                        "from_entity": relation.from_entity,
                        "to_entity": relation.to_entity,
                        "relation_type": relation.relation_type,
                    },
                    f,
                )
                f.write("\n")

            # Ensure the file is flushed and synced
            f.flush()
            os.fsync(f.fileno())

    def create_entities(self, entities: list[dict[str, str | list[str]]]) -> str:
        """Create new entities in the graph.

        Args:
            entities: List of entity dictionaries.

        Returns:
            Success message or error string.
        """
        # First check if any entities already exist
        for entity_data in entities:
            if entity_data["name"] in self.entities:
                return f"Entity already exists: {entity_data['name']}"

        # If all entities are new, create them
        for entity_data in entities:
            self.entities[entity_data["name"]] = Entity(
                name=entity_data["name"],
                entity_type=entity_data["entity_type"],
                observations=entity_data.get("observations", []),
            )

        self._save_graph()
        return "Successfully created entities"

    def create_relations(self, relations: list[dict[str, str]]) -> str:
        """Create new relations between entities.

        Args:
            relations: List of relation dictionaries.

        Returns:
            Success message or error string.
        """
        for relation_data in relations:
            if relation_data["from_entity"] not in self.entities or relation_data["to_entity"] not in self.entities:
                return f"""One or both entities not found:
                        {relation_data["from_entity"]},
                        {relation_data["to_entity"]}"""

            self.relations.append(
                Relation(
                    from_entity=relation_data["from_entity"],
                    to_entity=relation_data["to_entity"],
                    relation_type=relation_data["relation_type"],
                )
            )

        self._save_graph()
        return "Successfully created relations"

    def add_observations(self, observations: list[dict[str, str | list[str]]]) -> str:
        """Add observations to existing entities.

        Args:
            observations: List of observation dictionaries.

        Returns:
            Success message or error string.
        """
        # First check if all entities exist
        for obs_data in observations:
            if obs_data["entity_name"] not in self.entities:
                return f"Entity not found: {obs_data['entity_name']}"

        # If all entities exist, add observations
        for obs_data in observations:
            entity = self.entities[obs_data["entity_name"]]
            # Ensure we're extending the list, not replacing it
            entity.observations.extend(obs_data["contents"])

        self._save_graph()
        return "Successfully added observations"

    def delete_entities(self, entity_names: list[str]) -> str:
        """Delete entities and their relations.

        Args:
            entity_names: List of entity names to delete.

        Returns:
            Success message or error string.
        """
        for name in entity_names:
            if name in self.entities:
                del self.entities[name]
                # Remove related relations
                self.relations = [r for r in self.relations if name not in (r.from_entity, r.to_entity)]

        self._save_graph()
        return "Successfully deleted entities"

    def delete_observations(self, deletions: list[dict[str, str]]) -> str:
        """Delete specific observations from entities.

        Args:
            deletions: List of deletion dictionaries.

        Returns:
            Success message or error string.
        """
        for del_data in deletions:
            if del_data["entity_name"] not in self.entities:
                return f"Entity not found: {del_data['entity_name']}"

            entity = self.entities[del_data["entity_name"]]
            entity.observations = [obs for obs in entity.observations if obs != del_data["observation"]]

        self._save_graph()
        return "Successfully deleted observations"

    def delete_relations(self, relations: list[dict[str, str]]) -> str:
        """Delete specific relations from the graph.

        Args:
            relations: List of relation dictionaries.

        Returns:
            Success message or error string.
        """
        # First check if all relations exist
        for rel_data in relations:
            if not any(
                r.from_entity == rel_data["from_entity"]
                and r.to_entity == rel_data["to_entity"]
                and r.relation_type == rel_data["relation_type"]
                for r in self.relations
            ):
                return f"Relation not found: {rel_data['from_entity']} -> {rel_data['to_entity']}"

        # If all relations exist, delete them
        for rel_data in relations:
            self.relations = [
                r
                for r in self.relations
                if not (
                    r.from_entity == rel_data["from_entity"]
                    and r.to_entity == rel_data["to_entity"]
                    and r.relation_type == rel_data["relation_type"]
                )
            ]

        self._save_graph()
        return "Successfully deleted relations"

    def read_graph(self) -> dict[str, dict[str, dict] | list[dict]]:
        """Read the entire knowledge graph.

        Returns:
            Dictionary containing all entities and relations.
        """
        return {
            "entities": {
                name: {
                    "entity_type": entity.entity_type,
                    "observations": entity.observations,
                }
                for name, entity in self.entities.items()
            },
            "relations": [
                {
                    "from_entity": r.from_entity,
                    "to_entity": r.to_entity,
                    "relation_type": r.relation_type,
                }
                for r in self.relations
            ],
        }

    def search_nodes(self, query: str) -> dict[str, dict[str, dict] | list[dict]]:
        """Search for nodes based on query.

        Args:
            query: Search query string.

        Returns:
            Dictionary containing matching entities and their relations.
        """
        query = query.lower()
        matching_entities = {}

        # Search in entity names and types
        for name, entity in self.entities.items():
            if query in name.lower() or query in entity.entity_type.lower():
                matching_entities[name] = entity
                continue

            # Search in observations
            for obs in entity.observations:
                if query in obs.lower():
                    matching_entities[name] = entity
                    break

        # Get relations for matching entities
        matching_relations = [
            r for r in self.relations if r.from_entity in matching_entities or r.to_entity in matching_entities
        ]

        return {
            "entities": {
                name: {
                    "entity_type": entity.entity_type,
                    "observations": entity.observations,
                }
                for name, entity in matching_entities.items()
            },
            "relations": [
                {
                    "from_entity": r.from_entity,
                    "to_entity": r.to_entity,
                    "relation_type": r.relation_type,
                }
                for r in matching_relations
            ],
        }

    def open_nodes(self, names: list[str]) -> dict[str, dict[str, dict] | list[dict]]:
        """Open specific nodes by name.

        Args:
            names: List of entity names to retrieve.

        Returns:
            Dictionary containing requested entities and their relations.
        """
        requested_entities = {name: self.entities[name] for name in names if name in self.entities}

        requested_relations = [
            r for r in self.relations if r.from_entity in requested_entities or r.to_entity in requested_entities
        ]

        return {
            "entities": {
                name: {
                    "entity_type": entity.entity_type,
                    "observations": entity.observations,
                }
                for name, entity in requested_entities.items()
            },
            "relations": [
                {
                    "from_entity": r.from_entity,
                    "to_entity": r.to_entity,
                    "relation_type": r.relation_type,
                }
                for r in requested_relations
            ],
        }
