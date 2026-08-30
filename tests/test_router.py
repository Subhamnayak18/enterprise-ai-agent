from app.agents.router import deterministic_route

def test_routes():
    assert deterministic_route("What does the supplier SLA policy require?")=="rag"
    assert deterministic_route("Which five suppliers have the lowest rate?")=="sql"
    assert deterministic_route("Which suppliers currently violate SLA and what action should procurement take?")=="both"
    assert deterministic_route("Assess risk score for SUP001")=="business"
    assert deterministic_route("Generate escalation report for SUP001")=="report"
