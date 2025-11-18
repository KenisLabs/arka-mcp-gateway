import os
from typing import Optional
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

app = FastAPI()

CURR_DIR = os.getcwd()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


class CodePayload(BaseModel):
    code: str
    token_context: Optional[str] = None  # Encrypted token bundle


EXEC_WRAPPER = '''
import asyncio

async def _exec_wrapper():
    result = await run()
    if result is not None:
        print(result)

asyncio.run(_exec_wrapper())
'''


@app.post("/execute")
async def execute_code(payload: CodePayload):
    import subprocess
    import sys
    import tempfile
    import textwrap
    import json

    # Prepare environment variables
    env_vars = {"PYTHONPATH": CURR_DIR}

    # Decrypt and add token context if provided
    if payload.token_context:
        try:
            from gateway.token_context import decrypt_token_context

            # Decrypt the token context
            context = decrypt_token_context(payload.token_context)

            # Pass decrypted context as environment variable
            env_vars["MCP_TOKEN_CONTEXT"] = json.dumps(context)

        except Exception as e:
            return {"error": f"Failed to decrypt token context: {str(e)}"}

    # Write the user code to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tmp:
        # Remove any common leading whitespace and preserve newlines
        dedented_code = textwrap.dedent(json.loads(payload.code))
        tmp.write(dedented_code + "\n" + EXEC_WRAPPER)
        tmp.flush()
        script_path = tmp.name

    try:
        # Launch a separate Python process to run the script
        process = subprocess.Popen(
            [sys.executable, script_path],
            env=env_vars,  # Pass environment with token context
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()

        return {"result": stdout, "error": stderr}
    except Exception as e:
        return {"error": str(e)}
    finally:
        os.remove(script_path)


# if __name__ == "__main__":
#     uvicorn.run("worker:app", host="0.0.0.0", port=8001, reload=True)
