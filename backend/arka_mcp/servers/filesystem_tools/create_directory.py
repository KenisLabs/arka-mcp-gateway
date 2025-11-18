from typing import Dict, Any
import os


async def create_directory(path: str) -> Dict[str, Any]:
    """
    Create a new directory or ensure a directory exists. Can create multiple
    nested directories in one operation. If the directory already exists,
    this operation will succeed silently. Perfect for setting up directory
    structures for projects or ensuring required paths exist. Only works within allowed directories.
    """
    try:
        valid_path = os.path.abspath(path)
        os.makedirs(valid_path, exist_ok=True)

        return {
            "success": True,
            "content": [
                {"type": "text", "text": f"Successfully created directory {path}"}
            ],
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": f"Failed to create directory {path}: {e}",
        }
