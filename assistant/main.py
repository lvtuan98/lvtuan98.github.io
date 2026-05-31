from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="AI Chat Assistant")

allowed_origins = os.getenv(
    "CORS_ORIGINS", "https://lvtuan98.github.io,http://localhost:4000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list[dict]


@app.post("/api/chat")
async def chat(req: ChatRequest):
    from agent import stream_agent_response

    async def generate():
        async for token in stream_agent_response(req.messages):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/health")
async def health():
    return {"status": "ok", "type": "langgraph-agent"}
