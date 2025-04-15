"""Memory server implementation using a knowledge graph.

This module provides a persistent memory implementation using a local knowledge graph.
"""

import logging

from mcp.server.fastmcp import FastMCP

from ontology.knowledge_graph import KnowledgeGraph

# Set up MCP
mcp = FastMCP("memory")
logger = logging.getLogger(__name__)


class GraphManager:
    """Singleton manager for the knowledge graph instance."""

    _instance = None
    _graph: KnowledgeGraph | None = None

    def __new__(cls) -> "GraphManager":
        """Ensure only one instance of GraphManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_graph(self) -> KnowledgeGraph:
        """Get the graph instance, creating it if it doesn't exist."""
        if self._graph is None:
            self._graph = KnowledgeGraph()
        return self._graph

    def clear_graph(self) -> None:
        """Clear the graph instance."""
        if self._graph is not None:
            self._graph.clear()
            self._graph = KnowledgeGraph()


# Create the singleton instance
graph_manager = GraphManager()


def get_graph() -> KnowledgeGraph:
    """Get the global graph instance."""
    return graph_manager.get_graph()


def clear_graph() -> None:
    """Clear the global graph instance."""
    graph_manager.clear_graph()


@mcp.tool()
async def create_entities(entities: list[dict[str, str | list[str]]]) -> str:
    """Create new entities in the knowledge graph.

    Args:
        entities: List of entity dictionaries.

    Returns:
        Success message or error string.
    """
    return get_graph().create_entities(entities)


@mcp.tool()
async def create_relations(relations: list[dict[str, str]]) -> str:
    """Create new relations between entities.

    Args:
        relations: List of relation dictionaries.

    Returns:
        Success message or error string.
    """
    return get_graph().create_relations(relations)


@mcp.tool()
async def add_observations(observations: list[dict[str, str | list[str]]]) -> str:
    """Add observations to existing entities.

    Args:
        observations: List of observation dictionaries.

    Returns:
        Success message or error string.
    """
    return get_graph().add_observations(observations)


@mcp.tool()
async def delete_entities(entity_names: list[str]) -> str:
    """Delete entities and their relations.

    Args:
        entity_names: List of entity names to delete.

    Returns:
        Success message or error string.
    """
    return get_graph().delete_entities(entity_names)


@mcp.tool()
async def delete_observations(deletions: list[dict[str, str]]) -> str:
    """Delete specific observations from entities.

    Args:
        deletions: List of deletion dictionaries.

    Returns:
        Success message or error string.
    """
    return get_graph().delete_observations(deletions)


@mcp.tool()
async def delete_relations(relations: list[dict[str, str]]) -> str:
    """Delete specific relations from the graph.

    Args:
        relations: List of relation dictionaries.

    Returns:
        Success message or error string.
    """
    return get_graph().delete_relations(relations)


@mcp.tool()
async def read_graph() -> dict[str, dict[str, dict] | list[dict]]:
    """Read the entire knowledge graph.

    Returns:
        Dictionary containing all entities and relations.
    """
    return get_graph().read_graph()


@mcp.tool()
async def search_nodes(query: str) -> dict[str, dict[str, dict] | list[dict]]:
    """Search for nodes by name or observation content.

    Args:
        query: Search string.

    Returns:
        Dictionary containing matching entities and their relations.
    """
    return get_graph().search_nodes(query)


@mcp.tool()
async def open_nodes(names: list[str]) -> dict[str, dict[str, dict] | list[dict]]:
    """Open specific nodes and their relations.

    Args:
        names: List of entity names to open.

    Returns:
        Dictionary containing specified entities and their relations.
    """
    return get_graph().open_nodes(names)


def main() -> None:
    """Entry point for the memory server."""
    logger.info("Memory server starting...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
