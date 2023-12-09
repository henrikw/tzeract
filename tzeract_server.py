#!/usr/bin/python3 -u

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import List
from pydantic import BaseModel
import asyncio
import json
import subprocess

app = FastAPI()

sleep_seconds = 0


class CommandRequest(BaseModel):
    command: str
    args: List[str] = []  # "List" needed when python 3.8 (not 3.9).


async def run_command(command, args):
    process = await asyncio.create_subprocess_exec(
        command, *args,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    print(f"Sleeping {sleep_seconds} seconds...")
    await asyncio.sleep(sleep_seconds)
    return stdout, stderr, process.returncode


@app.post("/execute-command")
async def execute_command(request: CommandRequest):
    print("Here1!!!")
    try:
        stdout, stderr, returncode = await run_command(request.command, request.args)
    except Exception as e:
        print(f"Here3!!! {e}")
        return JSONResponse(status_code=500, content={"detail": "Command failed: 500"})
        # raise HTTPException(status_code=500, detail=f"Command failed: 500")

    print("Here2!!!")
    if returncode != 0:
        raise HTTPException(status_code=400, detail=f"Command failed: {stderr.decode().strip()}")
    return {"output": stdout.decode().splitlines()}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    print(f"### in http_exception_handler, exc.status_code={exc.status_code}, exc.detail={exc.detail}")
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
