from typing import Any, Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str
    version: str
    environment: str
    database: Literal["connected", "unavailable"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    route: str
    answer: str
    tools_used: list[str] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    sql_query: str | None = None
    sql_result: list[dict[str, Any]] | None = None
    business_result: dict[str, Any] | None = None
    errors: list[str] = Field(default_factory=list)


class IndexResponse(BaseModel):
    chunks_indexed: int


class SourceResponse(BaseModel):
    sources: list[dict[str, Any]]
