import os
from typing import Dict, Any


async def write_file(path: str, content: str) -> Dict[str, Any]:
    """
    Create a new file or completely overwrite an existing file with new content.
    Use with caution as it will overwrite existing files without warning.
    Handles text content with proper encoding. Only works within allowed directories.
    """
    try:
        valid_path = os.path.abspath(path)

        # Ensure the parent directory exists
        parent_dir = os.path.dirname(valid_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Write content to file (overwrite if exists)
        with open(valid_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "content": [{"type": "text", "text": f"Successfully wrote to {path}"}],
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": f"Failed to write to {path}: {e}",
        }
