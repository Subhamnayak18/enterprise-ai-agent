from app.tools.supplier_risk import assess_supplier_risk

def test_low_risk():
    r=assess_supplier_risk(.98,.99,.005,0.5); assert r.level=="Low"; assert r.score<20

def test_critical_risk():
    r=assess_supplier_risk(.80,.82,.08,9,critical_incidents=1); assert r.level=="Critical"; assert r.score>=70

def test_risk_is_deterministic():
    a=assess_supplier_risk(.90,.91,.03,4,high_incidents=2); b=assess_supplier_risk(.90,.91,.03,4,high_incidents=2); assert a==b
