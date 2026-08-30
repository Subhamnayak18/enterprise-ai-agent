from datetime import date

from sqlalchemy import text

from app.database.connection import get_engine


def get_latest_supplier_metrics(supplier_id: str) -> dict | None:
    query = text("""
        SELECT s.supplier_id, s.supplier_name, s.supplier_status, s.rating,
               sp.period, sp.on_time_delivery_rate, sp.fill_rate, sp.defect_rate,
               sp.average_delay_days, sp.quality_score,
               COALESCE(q.critical_incidents, 0) AS critical_incidents,
               COALESCE(q.high_incidents, 0) AS high_incidents
        FROM suppliers s
        JOIN supplier_performance sp ON sp.supplier_id = s.supplier_id
        LEFT JOIN (
            SELECT supplier_id,
                   SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) AS critical_incidents,
                   SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) AS high_incidents
            FROM quality_incidents
            GROUP BY supplier_id
        ) q ON q.supplier_id = s.supplier_id
        WHERE s.supplier_id = :supplier_id
        ORDER BY sp.period DESC
        LIMIT 1
    """)
    with get_engine().connect() as conn:
        row = conn.execute(query, {"supplier_id": supplier_id}).mappings().first()
    return dict(row) if row else None


def list_sources() -> list[dict]:
    from app.rag.loader import load_documents
    return [doc.metadata for doc in load_documents()]
