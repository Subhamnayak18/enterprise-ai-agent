import csv
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy.orm import Session

from app.database.connection import get_engine
from app.database.schema import Base, Product, PurchaseOrder, QualityIncident, Supplier, SupplierPerformance, Warehouse

RAW = ROOT / "data" / "raw"


def rows(name):
    with (RAW / name).open(encoding="utf-8") as f:
        yield from csv.DictReader(f)


def main():
    engine = get_engine(); Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add_all([Supplier(**{**r,"rating":float(r["rating"])}) for r in rows("suppliers.csv")])
        s.add_all([Product(**{**r,"unit_cost":Decimal(r["unit_cost"])}) for r in rows("products.csv")])
        s.add_all([Warehouse(**r) for r in rows("warehouses.csv")]); s.flush()
        s.add_all([SupplierPerformance(supplier_id=r["supplier_id"],period=date.fromisoformat(r["period"]),on_time_delivery_rate=float(r["on_time_delivery_rate"]),fill_rate=float(r["fill_rate"]),defect_rate=float(r["defect_rate"]),average_delay_days=float(r["average_delay_days"]),quality_score=float(r["quality_score"])) for r in rows("supplier_performance.csv")])
        s.add_all([QualityIncident(incident_id=r["incident_id"],supplier_id=r["supplier_id"],incident_date=date.fromisoformat(r["incident_date"]),severity=r["severity"],category=r["category"],description=r["description"],resolution_status=r["resolution_status"]) for r in rows("quality_incidents.csv")])
        orders=[]
        for r in rows("purchase_orders.csv"):
            orders.append(PurchaseOrder(po_id=r["po_id"],supplier_id=r["supplier_id"],product_id=r["product_id"],warehouse_id=r["warehouse_id"],order_date=date.fromisoformat(r["order_date"]),expected_delivery_date=date.fromisoformat(r["expected_delivery_date"]),actual_delivery_date=date.fromisoformat(r["actual_delivery_date"]) if r["actual_delivery_date"] else None,order_quantity=int(r["order_quantity"]),received_quantity=int(r["received_quantity"]) if r["received_quantity"] else None,order_value=Decimal(r["order_value"]),status=r["status"]))
        s.add_all(orders); s.commit()
    print("Database seeded successfully")

if __name__ == "__main__": main()
