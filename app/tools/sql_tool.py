import re
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.database.connection import get_engine
from app.llm.provider import LLMUnavailable, invoke_text
from app.prompts.prompts import SQL_SYSTEM

APPROVED_TABLES = {
    "suppliers",
    "purchase_orders",
    "supplier_performance",
    "quality_incidents",
    "products",
    "warehouses",
}
BLOCKED_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "revoke",
    "copy",
    "call",
}

SCHEMA_DESCRIPTION = """
suppliers(supplier_id, supplier_name, category, city, country, supplier_status, rating)
purchase_orders(po_id, supplier_id, product_id, warehouse_id, order_date, expected_delivery_date, actual_delivery_date, order_quantity, received_quantity, order_value, status)
supplier_performance(supplier_id, period, on_time_delivery_rate, fill_rate, defect_rate, average_delay_days, quality_score)
quality_incidents(incident_id, supplier_id, incident_date, severity, category, description, resolution_status)
products(product_id, product_name, category, unit_cost)
warehouses(warehouse_id, warehouse_name, city)
"""


@dataclass
class SQLExecution:
    sql: str
    rows: list[dict]
    row_count: int


def validate_sql(query: str) -> str:
    cleaned = query.strip().rstrip(";")
    if not cleaned:
        raise ValueError("SQL query is empty")
    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are not allowed")

    lowered = re.sub(r"\s+", " ", cleaned.lower())
    if not (lowered.startswith("select ") or lowered.startswith("with ")):
        raise ValueError("Only SELECT queries are allowed")

    words = set(re.findall(r"\b[a-z_]+\b", lowered))
    dangerous = words & BLOCKED_KEYWORDS
    if dangerous:
        raise ValueError(f"Blocked SQL keyword: {sorted(dangerous)[0]}")

    try:
        import sqlglot
        from sqlglot import exp

        parsed = sqlglot.parse_one(cleaned, read="postgres")
        destructive_types = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter)
        if any(isinstance(node, destructive_types) for node in parsed.walk()):
            raise ValueError("Destructive SQL is not allowed")
        tables = {table.name.lower() for table in parsed.find_all(exp.Table)}
        cte_names = {cte.alias_or_name.lower() for cte in parsed.find_all(exp.CTE)}
    except ImportError:
        tables = set(re.findall(r"(?:from|join)\s+([a-zA-Z_][\w]*)", cleaned, flags=re.I))
        tables = {table.lower() for table in tables}
        cte_names = set()
    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError("SQL could not be parsed safely") from exc

    unknown = tables - APPROVED_TABLES - cte_names
    if unknown:
        raise ValueError(f"Query references non-approved table(s): {', '.join(sorted(unknown))}")
    return cleaned


def enforce_row_limit(query: str, limit: int | None = None) -> str:
    limit = limit or get_settings().sql_row_limit
    match = re.search(r"\blimit\s+(\d+)", query, flags=re.I)
    if match:
        existing = int(match.group(1))
        if existing <= limit:
            return query
        return re.sub(r"\blimit\s+\d+", f"LIMIT {limit}", query, count=1, flags=re.I)
    return f"{query}\nLIMIT {limit}"


def execute_safe_sql(query: str) -> SQLExecution:
    safe = enforce_row_limit(validate_sql(query))
    engine = get_engine()
    try:
        with engine.connect() as conn:
            if engine.dialect.name == "postgresql":
                conn.execute(text(f"SET LOCAL statement_timeout = {int(get_settings().sql_query_timeout_ms)}"))
            result = conn.execute(text(safe))
            rows = [dict(row) for row in result.mappings().all()]
        return SQLExecution(sql=safe, rows=rows, row_count=len(rows))
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Database query failed: {type(exc).__name__}") from exc


def _development_sql_fallback(question: str) -> str:
    q = question.lower()
    latest_period = "(SELECT MAX(period) FROM supplier_performance)"

    if "lowest" in q and ("on-time" in q or "on time" in q or "otd" in q):
        return f"""SELECT s.supplier_id, s.supplier_name, sp.on_time_delivery_rate
FROM supplier_performance sp
JOIN suppliers s ON s.supplier_id = sp.supplier_id
WHERE sp.period = {latest_period}
ORDER BY sp.on_time_delivery_rate ASC
LIMIT 5"""

    if "sla" in q and ("violate" in q or "below" in q or "current" in q):
        return f"""SELECT s.supplier_id, s.supplier_name, sp.on_time_delivery_rate
FROM supplier_performance sp
JOIN suppliers s ON s.supplier_id = sp.supplier_id
WHERE sp.period = {latest_period} AND sp.on_time_delivery_rate < 0.95
ORDER BY sp.on_time_delivery_rate ASC"""

    if "watchlist" in q:
        return "SELECT supplier_id, supplier_name, rating FROM suppliers WHERE supplier_status = 'Watchlist' ORDER BY rating ASC"

    if "critical" in q and "incident" in q:
        return """SELECT s.supplier_id, s.supplier_name, COUNT(*) AS critical_incidents
FROM quality_incidents q
JOIN suppliers s ON s.supplier_id = q.supplier_id
WHERE q.severity = 'Critical'
GROUP BY s.supplier_id, s.supplier_name
ORDER BY critical_incidents DESC"""

    if "open purchase" in q:
        return "SELECT COUNT(*) AS open_purchase_orders FROM purchase_orders WHERE status = 'Open'"

    if "delayed purchase" in q:
        return "SELECT COUNT(*) AS delayed_purchase_orders FROM purchase_orders WHERE status = 'Delayed'"

    raise RuntimeError(
        "No LLM API key is configured and this question has no development SQL template. "
        "Configure OPENAI_API_KEY for general natural-language SQL."
    )


def generate_sql(question: str) -> str:
    prompt = f"Approved schema:\n{SCHEMA_DESCRIPTION}\nQuestion: {question}"
    try:
        raw = invoke_text(SQL_SYSTEM, prompt).strip().strip("`")
        if raw.lower().startswith("sql\n"):
            raw = raw[4:]
        return raw.strip()
    except LLMUnavailable:
        return _development_sql_fallback(question)


def answer_sql(question: str) -> SQLExecution:
    return execute_safe_sql(generate_sql(question))
