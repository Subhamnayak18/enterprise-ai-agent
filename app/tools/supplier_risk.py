from dataclasses import dataclass, asdict


@dataclass
class SupplierRiskResult:
    score: int
    level: str
    reasons: list[str]
    components: dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)


def assess_supplier_risk(
    on_time_delivery_rate: float,
    fill_rate: float,
    defect_rate: float,
    average_delay_days: float,
    critical_incidents: int = 0,
    high_incidents: int = 0,
) -> SupplierRiskResult:
    """Project-specific deterministic risk rules; not an industry standard."""
    components = {"delivery": 0, "quality": 0, "fulfilment": 0, "incidents": 0}
    reasons = []

    if on_time_delivery_rate < 0.85:
        components["delivery"] = 30
        reasons.append("On-time delivery is below 85%")
    elif on_time_delivery_rate < 0.92:
        components["delivery"] = 20
        reasons.append("On-time delivery is below 92%")
    elif on_time_delivery_rate < 0.96:
        components["delivery"] = 10
        reasons.append("On-time delivery is below 96%")

    if average_delay_days > 7:
        components["delivery"] = min(35, components["delivery"] + 5)
        reasons.append("Average delay exceeds 7 days")

    if defect_rate > 0.05:
        components["quality"] = 25
        reasons.append("Defect rate exceeds 5%")
    elif defect_rate > 0.025:
        components["quality"] = 15
        reasons.append("Defect rate exceeds 2.5%")
    elif defect_rate > 0.01:
        components["quality"] = 7
        reasons.append("Defect rate exceeds 1%")

    if fill_rate < 0.88:
        components["fulfilment"] = 20
        reasons.append("Fill rate is below 88%")
    elif fill_rate < 0.94:
        components["fulfilment"] = 12
        reasons.append("Fill rate is below 94%")
    elif fill_rate < 0.97:
        components["fulfilment"] = 5
        reasons.append("Fill rate is below 97%")

    if critical_incidents > 0:
        components["incidents"] = 25
        reasons.append(f"{critical_incidents} critical quality incident(s) recorded")
    elif high_incidents >= 2:
        components["incidents"] = 15
        reasons.append(f"{high_incidents} high-severity quality incidents recorded")
    elif high_incidents == 1:
        components["incidents"] = 8
        reasons.append("One high-severity quality incident recorded")

    score = min(100, sum(components.values()))
    if score >= 70:
        level = "Critical"
    elif score >= 45:
        level = "High"
    elif score >= 20:
        level = "Moderate"
    else:
        level = "Low"

    if not reasons:
        reasons.append("Current KPIs are within project-defined risk thresholds")
    return SupplierRiskResult(score=score, level=level, reasons=reasons, components=components)
