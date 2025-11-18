"""
MCP Server Registry - Manages MCP server metadata.

Loads and provides access to available MCP server definitions.
"""
import json
from pathlib import Path
from typing import List, Optional
from .models import MCPServerMetadata


class ServerRegistry:
    """
    Registry for MCP server metadata.

    Loads static metadata about available MCP servers from shared/mcp_servers.json
    and provides methods to query this information.
    """

    def __init__(self):
        """Initialize the server registry"""
        self._server_metadata: List[MCPServerMetadata] = []
        self._load_server_metadata()

    def _load_server_metadata(self):
        """Load available MCP servers from shared/mcp_servers.json"""
        # Shared directory is now inside backend/shared
        metadata_path = Path(__file__).parent.parent / "shared" / "mcp_servers.json"

        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                self._server_metadata = [
                    MCPServerMetadata(**server)
                    for server in data.get("servers", [])
                ]
        except FileNotFoundError:
            print(f"Warning: MCP servers metadata file not found at {metadata_path}")
            self._server_metadata = []
        except Exception as e:
            print(f"Error loading MCP servers metadata: {e}")
            self._server_metadata = []

    def get_available_servers(self) -> List[MCPServerMetadata]:
        """
        Get list of all available MCP servers from metadata.

        Returns:
            List of MCPServerMetadata objects
        """
        return self._server_metadata

    def get_server_metadata(self, server_id: str) -> Optional[MCPServerMetadata]:
        """
        Get metadata for a specific server.

        Args:
            server_id: The unique identifier of the server

        Returns:
            MCPServerMetadata if found, None otherwise
        """
        return next(
            (server for server in self._server_metadata if server.id == server_id),
            None
        )


# Global registry instance
_registry: Optional[ServerRegistry] = None


def get_registry() -> ServerRegistry:
    """
    Get the global server registry instance.
    Creates it if it doesn't exist (singleton pattern).

    Returns:
        The global ServerRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ServerRegistry()
    return _registry
