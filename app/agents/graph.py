import json
import re
from uuid import uuid4

from app.agents.router import route_query
from app.agents.state import AgentState
from app.database.repository import get_latest_supplier_metrics
from app.llm.provider import LLMUnavailable, invoke_text
from app.prompts.prompts import SYNTHESIS_SYSTEM
from app.tools.knowledge_tool import answer_knowledge
from app.tools.report_tool import generate_escalation_report
from app.tools.sql_tool import answer_sql
from app.tools.supplier_risk import assess_supplier_risk


def _extract_supplier_id(query: str) -> str | None:
    match = re.search(r"\bSUP\d{3}\b", query.upper())
    return match.group(0) if match else None


def _rag(state: AgentState) -> AgentState:
    result = answer_knowledge(state["user_query"])
    return {
        **state,
        "final_answer": result["answer"],
        "sources": result["sources"],
        "tools_used": ["rag"],
    }


def _sql(state: AgentState) -> AgentState:
    result = answer_sql(state["user_query"])
    return {
        **state,
        "final_answer": json.dumps(result.rows, default=str, indent=2),
        "sql_query": result.sql,
        "sql_result": result.rows,
        "tools_used": ["sql"],
    }


def _both(state: AgentState) -> AgentState:
    sql = answer_sql(state["user_query"])
    policy = answer_knowledge(state["user_query"])
    payload = (
        "Operational data:\n"
        + json.dumps(sql.rows, default=str)
        + "\n\nPolicy evidence:\n"
        + policy["answer"]
    )
    try:
        final = invoke_text(SYNTHESIS_SYSTEM, payload)
    except LLMUnavailable:
        final = (
            "Operational data:\n"
            + json.dumps(sql.rows, default=str, indent=2)
            + "\n\nPolicy evidence:\n"
            + policy["answer"]
        )
    return {
        **state,
        "final_answer": final,
        "sql_query": sql.sql,
        "sql_result": sql.rows,
        "sources": policy["sources"],
        "tools_used": ["sql", "rag"],
    }


def _business(state: AgentState) -> AgentState:
    supplier_id = _extract_supplier_id(state["user_query"])
    if not supplier_id:
        return {
            **state,
            "final_answer": "Please provide a supplier ID such as SUP001 for deterministic risk assessment.",
            "tools_used": ["supplier_risk"],
        }

    metrics = get_latest_supplier_metrics(supplier_id)
    if not metrics:
        return {
            **state,
            "final_answer": f"Supplier {supplier_id} was not found.",
            "tools_used": ["supplier_risk"],
        }

    risk = assess_supplier_risk(
        float(metrics["on_time_delivery_rate"]),
        float(metrics["fill_rate"]),
        float(metrics["defect_rate"]),
        float(metrics["average_delay_days"]),
        int(metrics["critical_incidents"]),
        int(metrics["high_incidents"]),
    )
    answer = f"{supplier_id} risk: {risk.level} ({risk.score}/100). Reasons: " + "; ".join(risk.reasons)
    return {
        **state,
        "final_answer": answer,
        "business_result": risk.to_dict(),
        "tools_used": ["supplier_risk"],
    }


def _report(state: AgentState) -> AgentState:
    supplier_id = _extract_supplier_id(state["user_query"])
    if not supplier_id:
        return {
            **state,
            "final_answer": "Please provide a supplier ID such as SUP001 to generate an escalation report.",
            "tools_used": ["report"],
        }
    report = generate_escalation_report(supplier_id)
    return {
        **state,
        "final_answer": json.dumps(report, default=str, indent=2),
        "business_result": report,
        "sources": report.get("sources", []),
        "tools_used": ["report", "supplier_risk", "rag"],
    }


NODES = {
    "rag": _rag,
    "sql": _sql,
    "both": _both,
    "business": _business,
    "report": _report,
}


def run_agent(query: str, conversation_id: str | None = None) -> AgentState:
    route = route_query(query)
    state: AgentState = {
        "user_query": query,
        "conversation_id": conversation_id or str(uuid4()),
        "route": route,
        "errors": [],
    }
    try:
        return NODES[route](state)
    except Exception as exc:
        return {
            **state,
            "final_answer": "The request could not be completed safely.",
            "errors": [str(exc)],
            "tools_used": [],
        }


def build_langgraph():
    """Build the explicit LangGraph used by the API."""
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(AgentState)

    def route_node(state: AgentState) -> AgentState:
        return {**state, "route": route_query(state["user_query"])}

    graph.add_node("route", route_node)
    for name, fn in NODES.items():
        graph.add_node(name, fn)
    graph.add_edge(START, "route")
    graph.add_conditional_edges("route", lambda state: state["route"], {name: name for name in NODES})
    for name in NODES:
        graph.add_edge(name, END)
    return graph.compile()


def invoke_agent(query: str, conversation_id: str | None = None) -> AgentState:
    try:
        graph = build_langgraph()
        return graph.invoke(
            {
                "user_query": query,
                "conversation_id": conversation_id or str(uuid4()),
                "errors": [],
            }
        )
    except ImportError:
        return run_agent(query, conversation_id)
