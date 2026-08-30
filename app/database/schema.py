from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Supplier(Base):
    __tablename__ = "suppliers"
    supplier_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    supplier_name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    city: Mapped[str] = mapped_column(String(60), nullable=False)
    country: Mapped[str] = mapped_column(String(60), nullable=False, default="India")
    supplier_status: Mapped[str] = mapped_column(String(30), nullable=False)
    rating: Mapped[float | None] = mapped_column(Float)


class Product(Base):
    __tablename__ = "products"
    product_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)


class Warehouse(Base):
    __tablename__ = "warehouses"
    warehouse_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    warehouse_name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(60), nullable=False)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    po_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.supplier_id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id"), index=True)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.warehouse_id"), index=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expected_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date)
    order_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    received_quantity: Mapped[int | None] = mapped_column(Integer)
    order_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)


class SupplierPerformance(Base):
    __tablename__ = "supplier_performance"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.supplier_id"), index=True)
    period: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    on_time_delivery_rate: Mapped[float] = mapped_column(Float, nullable=False)
    fill_rate: Mapped[float] = mapped_column(Float, nullable=False)
    defect_rate: Mapped[float] = mapped_column(Float, nullable=False)
    average_delay_days: Mapped[float] = mapped_column(Float, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)


class QualityIncident(Base):
    __tablename__ = "quality_incidents"
    incident_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.supplier_id"), index=True)
    incident_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(30), nullable=False)
