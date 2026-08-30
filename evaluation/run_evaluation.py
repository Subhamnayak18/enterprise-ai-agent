import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agents.router import deterministic_route
from app.rag.retriever import retrieve
from app.tools.sql_tool import validate_sql

RETRIEVAL_CHECKS = [
    ("What happens when OTD is below 90%?", "Supplier Delivery SLA"),
    ("What are Level 2 and Level 3 vendor escalation rules?", "Vendor Escalation Policy"),
    ("What approval is needed for a purchase order above INR 1,000,000?", "Purchase Order Approval Policy"),
    ("Critical quality incident containment within 24 hours root-cause analysis", "Quality Incident Management SOP"),
    ("When can a supplier be removed from Watchlist?", "Supplier Performance Management Policy"),
    ("When is competitive quotation required?", "Procurement SOP"),
    ("When should safety stock changes be reviewed?", "Inventory Replenishment Policy"),
]

UNSAFE_SQL = [
    "DELETE FROM suppliers",
    "DROP TABLE suppliers",
    "UPDATE suppliers SET rating = 5",
    "INSERT INTO suppliers VALUES ('X')",
    "ALTER TABLE suppliers ADD COLUMN secret TEXT",
    "SELECT * FROM payroll",
]


def main():
    questions = json.loads((ROOT / "evaluation/questions.json").read_text())

    route_correct = 0
    latencies = []
    for item in questions:
        start = time.perf_counter()
        route = deterministic_route(item["question"])
        latencies.append((time.perf_counter() - start) * 1000)
        route_correct += route == item["category"]

    retrieval_hits = 0
    for question, expected_source in RETRIEVAL_CHECKS:
        names = {result.metadata.get("document_name") for result in retrieve(question, top_k=3)}
        retrieval_hits += expected_source in names

    rejected = 0
    for query in UNSAFE_SQL:
        try:
            validate_sql(query)
        except ValueError:
            rejected += 1

    result = {
        "routing_questions": len(questions),
        "routing_accuracy": round(route_correct / len(questions), 4),
        "avg_deterministic_router_latency_ms": round(sum(latencies) / len(latencies), 3),
        "retrieval_checks": len(RETRIEVAL_CHECKS),
        "retrieval_source_hit_at_3": round(retrieval_hits / len(RETRIEVAL_CHECKS), 4),
        "unsafe_sql_checks": len(UNSAFE_SQL),
        "unsafe_sql_rejection_rate": round(rejected / len(UNSAFE_SQL), 4),
        "notes": "Measured on the included synthetic policy/data project environment. Routing set is curated and not an external benchmark.",
    }
    (ROOT / "evaluation/results.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
