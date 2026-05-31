from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator

from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.prebuilt import create_react_agent

from llm import get_chat_model
from tools import ALL_TOOLS

KNOWLEDGE_PATH = Path(__file__).parent / "knowledge.md"

SYSTEM_PROMPT = """\
You are a friendly AI assistant on Van-Tuan Le's personal homepage.

Your role:
- Answer visitors' questions about Van-Tuan Le based on the knowledge base below.
- If you don't know the answer, say so honestly.
- Keep answers concise and helpful.
- If a visitor wants to contact Van-Tuan Le, use the get_contact_info tool first, \
then offer to send a message using the send_email tool.
- Before sending an email, always confirm the visitor's name, email, and message.
- If information seems outdated, use the refresh_knowledge tool.

Knowledge base:
---
{knowledge}
---"""


def _load_system_prompt() -> str:
    knowledge = KNOWLEDGE_PATH.read_text(encoding="utf-8")
    return SYSTEM_PROMPT.format(knowledge=knowledge)


def create_agent_graph():
    """Create and return the LangGraph ReAct agent."""
    model = get_chat_model()
    system_prompt = _load_system_prompt()

    graph = create_react_agent(
        model=model,
        tools=ALL_TOOLS,
        prompt=system_prompt,
    )
    return graph


async def stream_agent_response(
    messages: list[dict],
) -> AsyncIterator[str]:
    """Stream the agent's response for a list of chat messages."""
    graph = create_agent_graph()

    lc_messages = []
    for msg in messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            from langchain_core.messages import AIMessage

            lc_messages.append(AIMessage(content=msg["content"]))

    async for event in graph.astream_events(
        {"messages": lc_messages},
        version="v2",
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                if isinstance(chunk.content, str):
                    yield chunk.content
                elif isinstance(chunk.content, list):
                    for part in chunk.content:
                        if isinstance(part, str):
                            yield part
                        elif isinstance(part, dict) and part.get("type") == "text":
                            yield part["text"]
