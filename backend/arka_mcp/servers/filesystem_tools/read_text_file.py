from typing import Dict, Any, Optional
import os
import subprocess


async def read_text_file(
    path: str, head: Optional[int] = None, tail: Optional[int] = None
) -> Dict[str, Any]:
    """
    Reads part of a text file using native UNIX `head`, `tail`, or `cat` commands.
    Efficient and simple—does not load the full file into memory.

    Args:
        path (str): Path to the text file.
        head (int, optional): Number of lines to read from the start.
        tail (int, optional): Number of lines to read from the end.
    Returns a dictionary with either:
      - "content": string containing requested lines of the file
      - "error": a string describing the problem

    Example content:
    {
        "content": "Line 1\nLine 2\nLine 3\n"
    }

    Example error:
    {
        "error": "File not found: jay_chou/song1.txt"
    }
    """
    if not os.path.exists(path):
        return {"error": f"File not found: {path}"}
    if not os.path.isfile(path):
        return {
            "error": f"Path is not a file: {path}",
        }

    try:
        if head is not None and head > 0:
            cmd = ["head", f"-n{head}", path]
        elif tail is not None and tail > 0:
            cmd = ["tail", f"-n{tail}", path]
        else:
            cmd = ["cat", path]  # Show complete file

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return {
                "error": result.stderr.strip() or "Command failed.",
            }

        return {"content": result.stdout}

    except Exception as e:
        return {"error": str(e)}
