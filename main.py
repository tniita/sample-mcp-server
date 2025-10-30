from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time

app = FastAPI()

def sse_generator():
    yield "event: message\ndata: Hello MCP Server\n\n"
    while True:
        time.sleep(2)
        yield f"event: ping\ndata: still alive\n\n"

@app.get("/mcp/")
async def mcp_messages():
    return "Hello World"