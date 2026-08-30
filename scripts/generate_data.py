from __future__ import annotations
import csv, random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"
random.seed(42)

CITIES = ["Bengaluru", "Mumbai", "Pune", "Hyderabad", "Chennai", "Delhi", "Ahmedabad", "Kolkata", "Jaipur", "Indore"]
CATEGORIES = ["Packaging", "Ingredients", "Dairy Inputs", "Edible Oils", "Spices", "Cleaning", "Maintenance"]
PREFIX = ["Apex", "Nova", "Green", "Prime", "Shakti", "Vertex", "Blue", "Reliable", "Sunrise", "Metro", "Sapphire", "Crown"]
SUFFIX = ["Industries", "Foods", "Supplies", "Materials", "Trading", "Enterprises"]


def write(name, rows, fields):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)


def main():
    suppliers=[]; profiles={}
    for i in range(1,51):
        sid=f"SUP{i:03d}"; quality=random.betavariate(6,2)
        profiles[sid]=quality
        suppliers.append({"supplier_id":sid,"supplier_name":f"{random.choice(PREFIX)} {random.choice(SUFFIX)} {i}","category":random.choice(CATEGORIES),"city":random.choice(CITIES),"country":"India","supplier_status":"Active" if quality>.28 else "Watchlist","rating":round(2.5+quality*2.4,1)})
    write("suppliers.csv",suppliers,suppliers[0].keys())

    products=[]
    for i in range(1,41):
        cat=random.choice(CATEGORIES[:5]); products.append({"product_id":f"PRD{i:03d}","product_name":f"{cat} Item {i}","category":cat,"unit_cost":round(random.uniform(30,1800),2)})
    write("products.csv",products,products[0].keys())

    warehouses=[{"warehouse_id":f"WH{i:02d}","warehouse_name":f"{city} Distribution Centre","city":city} for i,city in enumerate(["Mumbai","Delhi","Bengaluru","Kolkata","Hyderabad"],1)]
    write("warehouses.csv",warehouses,warehouses[0].keys())

    performance=[]
    today=date(2026,8,1)
    for sid,q in profiles.items():
        for m in range(12):
            period=(today.replace(day=1)-timedelta(days=30*m)).replace(day=1)
            shock=random.gauss(0,0.035)
            otd=max(.62,min(.995,.77+.22*q+shock))
            fill=max(.70,min(1,.82+.16*q+random.gauss(0,.025)))
            defect=max(.002,min(.11,.085*(1-q)+random.gauss(0,.008)))
            delay=max(0,12*(1-otd)+random.gauss(0,.8))
            quality_score=max(50,min(100,100-defect*320-random.uniform(0,4)))
            performance.append({"supplier_id":sid,"period":period.isoformat(),"on_time_delivery_rate":round(otd,4),"fill_rate":round(fill,4),"defect_rate":round(defect,4),"average_delay_days":round(delay,2),"quality_score":round(quality_score,1)})
    write("supplier_performance.csv",performance,performance[0].keys())

    incidents=[]
    incident_no=1
    for sid,q in profiles.items():
        count=max(0,int((1-q)*6+random.gauss(0,1)))
        for _ in range(count):
            sev=random.choices(["Low","Medium","High","Critical"],weights=[40,35,20,5 if q>.45 else 12])[0]
            d=today-timedelta(days=random.randint(0,365))
            incidents.append({"incident_id":f"QI{incident_no:04d}","supplier_id":sid,"incident_date":d.isoformat(),"severity":sev,"category":random.choice(["Packaging Damage","Contamination","Specification Deviation","Short Supply","Labelling"]),"description":f"{sev} supplier quality deviation identified during receiving inspection.","resolution_status":random.choices(["Closed","Corrective Action Open","Under Investigation"],weights=[60,25,15])[0]})
            incident_no+=1
    write("quality_incidents.csv",incidents,incidents[0].keys())

    pos=[]
    for i in range(1,801):
        sid=random.choice(list(profiles)); q=profiles[sid]; product=random.choice(products); wh=random.choice(warehouses)
        order=today-timedelta(days=random.randint(0,360)); expected=order+timedelta(days=random.randint(5,24))
        pending=random.random()<.08 and expected>today-timedelta(days=25)
        delay_days=max(-3,round(random.gauss((1-q)*6,3)))
        actual=None if pending else expected+timedelta(days=delay_days)
        qty=random.randint(100,5000); received=None if pending else max(0,round(qty*max(.75,min(1,random.gauss(.90+.09*q,.03)))))
        status="Open" if pending else ("Delayed" if actual>expected else "Delivered")
        pos.append({"po_id":f"PO{i:05d}","supplier_id":sid,"product_id":product["product_id"],"warehouse_id":wh["warehouse_id"],"order_date":order.isoformat(),"expected_delivery_date":expected.isoformat(),"actual_delivery_date":actual.isoformat() if actual else "","order_quantity":qty,"received_quantity":received if received is not None else "","order_value":round(qty*float(product["unit_cost"]),2),"status":status})
    write("purchase_orders.csv",pos,pos[0].keys())
    print(f"Generated {len(suppliers)} suppliers, {len(products)} products, {len(performance)} performance rows, {len(incidents)} incidents and {len(pos)} purchase orders")

if __name__ == "__main__": main()
