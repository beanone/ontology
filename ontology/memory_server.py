"""Memory server implementation using a knowledge graph.

This module provides a persistent memory implementation using a local knowledge graph.
"""

import logging
import threading
import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from ontology.knowledge_graph import KnowledgeGraph, MemoryError

# Set up MCP
mcp = FastMCP("memory")
logger = logging.getLogger(__name__)


@mcp.resource(uri="http://localhost/graph")
class KnowledgeGraphResource:
    """MCP Resource for accessing the knowledge graph."""

    def __init__(self):
        self.graph = get_graph()

    async def get_entities(self) -> dict:
        """Get all entities in the graph."""
        return self.graph.read_graph()["entities"]

    async def get_relations(self) -> list:
        """Get all relations in the graph."""
        return self.graph.read_graph()["relations"]


class GraphManager:
    """Singleton manager for the knowledge graph instance."""

    _instance = None
    _graph: KnowledgeGraph | None = None
    _lock = threading.Lock()

    def __new__(cls) -> "GraphManager":
        """Ensure only one instance of GraphManager exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def get_graph(self) -> KnowledgeGraph:
        """Get the graph instance, creating it if it doesn't exist."""
        if self._graph is None:
            with self._lock:
                if self._graph is None:
                    try:
                        self._graph = KnowledgeGraph()
                    except MemoryError as e:
                        logger.error("Failed to initialize knowledge graph: %s", str(e))
                        raise
        return self._graph

    def clear_graph(self) -> None:
        """Clear the graph instance."""
        with self._lock:
            if self._graph is not None:
                self._graph.clear()
                self._graph = None  # Reset to None so it's recreated on next get_graph()

    def save_graph(self) -> None:
        """Save the current graph state."""
        with self._lock:
            if self._graph is not None:
                self._graph.save()

    def load_graph(self) -> None:
        """Load the graph from storage."""
        with self._lock:
            if self._graph is None:
                self._graph = KnowledgeGraph()
            self._graph.load()


# Create the singleton instance
graph_manager = GraphManager()


def get_graph() -> KnowledgeGraph:
    """Get the global graph instance."""
    return graph_manager.get_graph()


def clear_graph() -> None:
    """Clear the global graph instance."""
    graph_manager.clear_graph()


@mcp.tool()
async def create_entities(entities: list[dict]) -> str:
    """Create new entities in the knowledge graph."""
    return get_graph().create_entities(entities)


@mcp.tool()
async def create_relations(relations: list[dict]) -> str:
    """Create new relations between entities."""
    return get_graph().create_relations(relations)


@mcp.tool()
async def add_observations(observations: list[dict[str, str | list[str]]]) -> str:
    """Add observations to existing entities."""
    return get_graph().add_observations(observations)


@mcp.tool()
async def delete_entities(entity_names: list[str]) -> str:
    """Delete entities and their relations."""
    return get_graph().delete_entities(entity_names)


@mcp.tool()
async def delete_observations(deletions: list[dict[str, str]]) -> str:
    """Delete specific observations from entities."""
    return get_graph().delete_observations(deletions)


@mcp.tool()
async def delete_relations(relations: list[dict[str, str]]) -> str:
    """Delete specific relations from the graph."""
    return get_graph().delete_relations(relations)


@mcp.tool()
async def read_graph() -> dict[str, dict[str, dict] | list[dict]]:
    """Read the entire knowledge graph."""
    return get_graph().read_graph()


@mcp.tool()
async def search_nodes(query: str) -> dict[str, dict[str, dict] | list[dict]]:
    """Search for nodes by name or observation content."""
    return get_graph().search_nodes(query)


@mcp.tool()
async def open_nodes(names: list[str]) -> dict[str, dict[str, dict] | list[dict]]:
    """Open specific nodes and their relations."""
    return get_graph().open_nodes(names)


def main() -> None:
    """Run the memory server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
