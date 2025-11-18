import os
from typing import Dict, Any, List, Optional
import fnmatch

from typing import Dict, Any, Optional, List
import os


async def list_directory(path: str, recursive: bool = False) -> Dict[str, Any]:
    """
    Get a detailed listing of all files and directories in a specified path.
    Each entry includes a 'name' and 'type' key:
      - 'name': the file or directory name
      - 'type': either 'file' or 'directory'
    Only works within allowed directories.

    Parameters:
        recursive (bool): If True, include all subdirectories recursively.

    Returns a dictionary with either:
      - "content": a list of entries, each with 'name' and 'type'
        Example:
            {
                "content": [
                    {"name": "song1.txt", "type": "file"},
                    {"name": "album", "type": "directory", "children": [...]}
                ]
            }
      OR
      - "error": a string describing the problem
        Example:
            {"error": "Path not found: test1/"}

    Output format:
    {
        "content": [{"name": "entry_name", "type": "file|directory", "children": [...]}, ...]
        OR
        "error": "Error message if something went wrong"
    }
    """

    def build_entries(current_path: str) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        try:
            for entry in sorted(os.listdir(current_path)):
                full_entry = os.path.join(current_path, entry)
                entry_type = "directory" if os.path.isdir(full_entry) else "file"
                entry_data: Dict[str, Any] = {"name": entry, "type": entry_type}
                if recursive and entry_type == "directory":
                    entry_data["children"] = build_entries(full_entry)
                result.append(entry_data)
        except Exception:
            pass
        return result

    try:
        valid_path = os.path.abspath(path)
        if not os.path.exists(valid_path):
            return {"error": f"Path not found: {path}"}
        if not os.path.isdir(valid_path):
            return {"error": f"Path is not a directory: {path}"}

        entries = build_entries(valid_path)
        return {"content": entries}

    except Exception as e:
        return {"error": str(e)}
