from app.database.repository import get_latest_supplier_metrics
from app.tools.knowledge_tool import answer_knowledge
from app.tools.supplier_risk import assess_supplier_risk


def generate_escalation_report(supplier_id: str) -> dict:
    metrics = get_latest_supplier_metrics(supplier_id)
    if not metrics:
        raise ValueError(f"Supplier {supplier_id} was not found")
    risk = assess_supplier_risk(
        on_time_delivery_rate=float(metrics["on_time_delivery_rate"]),
        fill_rate=float(metrics["fill_rate"]),
        defect_rate=float(metrics["defect_rate"]),
        average_delay_days=float(metrics["average_delay_days"]),
        critical_incidents=int(metrics["critical_incidents"]),
        high_incidents=int(metrics["high_incidents"]),
    )
    policy = answer_knowledge("What escalation action is required for a supplier with delivery or quality performance problems?")
    return {
        "supplier": {"supplier_id": metrics["supplier_id"], "supplier_name": metrics["supplier_name"]},
        "current_risk": risk.to_dict(),
        "operational_kpis": {
            "period": str(metrics["period"]),
            "on_time_delivery_rate": metrics["on_time_delivery_rate"],
            "fill_rate": metrics["fill_rate"],
            "defect_rate": metrics["defect_rate"],
            "average_delay_days": metrics["average_delay_days"],
            "quality_score": metrics["quality_score"],
        },
        "applicable_policy": policy["answer"],
        "sources": policy["sources"],
        "human_approval_required": True,
    }
