from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    user_query: str
    conversation_id: str
    route: str
    retrieved_documents: list[dict]
    sql_query: str
    sql_result: list[dict]
    business_result: dict
    sources: list[dict]
    errors: list[str]
    final_answer: str
    tools_used: list[str]
