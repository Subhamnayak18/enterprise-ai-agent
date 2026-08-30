from app.llm.provider import LLMUnavailable, invoke_text
from app.prompts.prompts import ROUTER_SYSTEM

ROUTES = {"rag", "sql", "both", "business", "report"}


def deterministic_route(query: str) -> str:
    q = query.lower()

    if any(term in q for term in ["escalation summary", "escalation report", "generate report"]):
        return "report"

    if ("sup" in q and "high risk" in q) or any(
        term in q
        for term in [
            "risk score",
            "risk level",
            "assess risk",
            "assess supplier risk",
            "supplier risk for",
            "deterministic supplier risk",
            "considered high risk",
        ]
    ):
        return "business"

    supplier_entity_request = "supplier" in q and any(q.startswith(prefix) for prefix in ["which ", "find ", "identify ", "list "])

    asks_for_entities_or_metrics = supplier_entity_request or any(
        term in q
        for term in [
            "which supplier",
            "which suppliers",
            "find suppliers",
            "identify suppliers",
            "list suppliers",
            "count ",
            "how many",
            "average ",
            "total ",
            "top ",
            "lowest",
            "highest",
            "by month",
            "by severity",
            "rating below",
            "open purchase",
            "delayed purchase",
            "purchase order value",
        ]
    )

    asks_for_policy_action = any(
        term in q
        for term in [
            "what action",
            "what should happen",
            "what approval",
            "what policy",
            "what recovery",
            "what human review",
            "what containment",
            "what escalation",
            "according to",
            "explain the escalation",
            "summarize the applicable",
            "process applies",
            "rule",
            "should procurement",
        ]
    )

    if asks_for_entities_or_metrics and asks_for_policy_action:
        return "both"

    policy_terms = [
        "policy",
        "sla",
        "sop",
        "guideline",
        "approval",
        "required response",
        "what should happen",
        "when does",
        "when can",
        "who reviews",
        "can the ai",
        "what information should",
        "what does closure",
        "how are customer-caused",
        "otd target",
    ]
    if any(term in q for term in policy_terms):
        return "rag"

    if asks_for_entities_or_metrics or any(
        term in q
        for term in ["current", "latest", "rate", "metric", "incident", "performance", "order value"]
    ):
        return "sql"

    return "rag"


def route_query(query: str) -> str:
    try:
        response = invoke_text(ROUTER_SYSTEM, query).strip().lower()
        return response if response in ROUTES else deterministic_route(query)
    except LLMUnavailable:
        return deterministic_route(query)
