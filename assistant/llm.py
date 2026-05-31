from __future__ import annotations

import os

from langchain_core.language_models import BaseChatModel


def get_chat_model() -> BaseChatModel:
    """Return a LangChain ChatModel based on the LLM_PROVIDER env var."""
    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            streaming=True,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            google_api_key=os.environ["GEMINI_API_KEY"],
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            streaming=True,
        )

    if provider == "nvidia":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=os.environ["NVIDIA_API_KEY"],
            base_url="https://inference-api.nvidia.com/v1",
            model=os.getenv("NVIDIA_MODEL", "nvidia/openai/gpt-oss-20b"),
            streaming=True,
        )

    if provider == "local":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key="ollama",
            base_url=os.getenv("LOCAL_LLM_URL", "http://localhost:11434") + "/v1",
            model=os.getenv("LOCAL_LLM_MODEL", "llama3.2"),
            streaming=True,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. "
        f"Choose from: openai, gemini, nvidia, local"
    )
