#!/usr/bin/python3 -u

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import List
from pydantic import BaseModel
import asyncio
import subprocess

app = FastAPI()

sleep_seconds = 5


class CommandRequest(BaseModel):
    command: str
    args: List[str] = []  # "List" needed when python 3.8 (not 3.9).


async def run_external_command(command, args):
    full_command = f"{command} {' '.join(args)}"
    # Run the command with shell expansion to make wildcard work.
    process = await asyncio.create_subprocess_shell(
        full_command,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    print(f"Before sleeping {sleep_seconds} seconds...")
    await asyncio.sleep(sleep_seconds)
    print(f"After sleeping {sleep_seconds} seconds...")
    return stdout, stderr, process.returncode


def valid_command(command):
    # Whitelisting which commands are allowed, to limit the risk of dangerous commands being run.
    # Allow 'lsx' in order to be able to test with an invalid external command.
    return command in ('ls', 'lsx', 'mkdir', 'touch')


@app.post("/execute-command")
async def execute_command(request: CommandRequest):
    if not valid_command(request.command):
        return JSONResponse(status_code=400, content={"detail": "Command not allowed"})

    try:
        stdout, stderr, return_code = await run_external_command(request.command, request.args)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Command failed: 500"})

    if return_code != 0:
        error_detail = f"Command failed (return code: {return_code})"
        message = stderr.decode().strip()
        if message:
            error_detail += f", {message}"
        return JSONResponse(status_code=400, content={"detail": error_detail})
    return {"output": stdout.decode().splitlines()}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"detail": "The URL does not exist"},
        )
    # Pass other HTTP exceptions as is
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
