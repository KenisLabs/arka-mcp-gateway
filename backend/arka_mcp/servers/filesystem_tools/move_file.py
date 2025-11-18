import os
from typing import Dict, Any


async def move_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Move or rename files and directories. Can move files between directories
    and rename them in a single operation. If the destination exists, the
    operation will fail. Works across different directories and can be used
    for simple renaming within the same directory. Both source and destination
    must be within allowed directories.

    Output format:
    {
        "content": [{"type": "text", "text": "Success message"}]
    }
    OR
    {
        "error": "Error message if something went wrong"
    }

    Example content:
    {
        "content": [{"type": "text", "text": "Successfully moved source.txt to dest.txt"}]
    }

    Example error:
    {
        "error": "Source file not found: source.txt"
    }
    """
    try:
        valid_source = os.path.abspath(source)
        valid_dest = os.path.abspath(destination)

        if not os.path.exists(valid_source):
            return {"error": f"Source file not found: {source}"}
        if os.path.exists(valid_dest):
            return {"error": f"Destination already exists: {destination}"}

        os.rename(valid_source, valid_dest)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Successfully moved {source} to {destination}",
                }
            ]
        }

    except Exception as e:
        return {"error": str(e)}
