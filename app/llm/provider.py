import json
from typing import Any

from app.core.config import get_settings


class LLMUnavailable(RuntimeError):
    pass


def llm_available() -> bool:
    settings = get_settings()
    return settings.llm_provider == "openai" and bool(settings.openai_api_key)


def get_chat_model():
    settings = get_settings()
    if not llm_available():
        raise LLMUnavailable("No LLM API key configured")
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=settings.llm_temperature,
    )


def get_embedding_model():
    settings = get_settings()
    if not llm_available():
        raise LLMUnavailable("No embedding API key configured")
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(model=settings.openai_embedding_model, api_key=settings.openai_api_key)


def invoke_text(system: str, user: str) -> str:
    model = get_chat_model()
    response = model.invoke([("system", system), ("human", user)])
    return str(response.content)
