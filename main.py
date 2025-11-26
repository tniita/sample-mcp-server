from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse


app = FastAPI()

@app.post("/")  # 例: ツール呼び出し用の POST
async def mcp_tool_echo(req: Request):
    # リクエストの id を返すのが JSON-RPC では自然（なければ適当に 1）
    try:
        body = await req.json()
        req_id = body.get("id", 1)
        # ここでは固定文字列 "Hello World" を MCP の result に包んで返す
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "output": "Hello World"
            }
        }
        return JSONResponse(content=payload, media_type="application/json")
    
    except Exception:
        # JSON-RPC  の error 形式で返す
        payload = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": "Invalid Request"}
        }
