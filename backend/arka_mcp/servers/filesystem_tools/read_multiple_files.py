from typing import Dict, Any, List
import os
import subprocess


async def read_multiple_files(paths: List[str]) -> Dict[str, Any]:
    """
    Read the contents of multiple files simultaneously.
    This is more efficient than reading files one by one when you need to
    analyze or compare multiple files. Each file's content is returned
    with its path as a reference. Failed reads for individual files won't
    stop the entire operation. Only works within allowed directories.

    Returns a dictionary with either:
      - "content": a list of objects containing 'path' and 'content' or 'error'
      - "error": a string describing the overall failure (only if all files fail)

    Example content:
    {
        "content": [
            {"path": "notes/todo.txt", "content": "Buy milk\nPlan trip\n"},
            {"path": "summary.txt", "error": "File not found: summary.txt"}
        ]
    }

    Example error:
    {
        "error": "No valid files could be read."
    }
    """
    results = []

    for path in paths:
        valid_path = os.path.abspath(path)
        if not os.path.exists(valid_path):
            results.append({"path": path, "error": f"File not found: {path}"})
            continue
        if not os.path.isfile(valid_path):
            results.append({"path": path, "error": f"Path is not a file: {path}"})
            continue

        try:
            cmd = ["cat", valid_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                results.append(
                    {"path": path, "error": result.stderr.strip() or "Command failed."}
                )
            else:
                results.append({"path": path, "content": result.stdout})
        except Exception as e:
            results.append({"path": path, "error": str(e)})

    # If all files failed, return overall error
    if all("error" in entry for entry in results):
        return {"error": "No valid files could be read."}

    return {"content": results}
