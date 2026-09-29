from app.services.risk_engine import RiskEngine
from app.models.complaint import ComplaintRecord, ProductDetails, ManufacturingDetails, ComplaintDetails

def test_sterile_product_breach_guardrail():
    """Verify sterile injectable breach is clamped to CRITICAL regardless of small quantity."""
    complaint = ComplaintRecord(
        product_batch=ProductDetails(
            product_name="Epinephrine Injection",
            product_grade_strength="1mg/mL, USP"
        ),
        manufacturing=ManufacturingDetails(
            batch_number="B24017",
            affected_quantity=1  # Even with 1 single unit!
        ),
        origin_customer=ComplaintDetails(
            complaint_type="Container Closure Leakage",
            complaint_description="Hospital pharmacy found leak around rubber stopper."
        )
    )

    risk = RiskEngine.evaluate(complaint=complaint)
    assert risk.severity == "CRITICAL"
    assert "P1" in risk.priority
    assert risk.risk_score >= 60
    assert risk.requires_regulatory_escalation is True
    assert any("quarantine" in action.lower() for action in risk.recommended_actions)
    assert "Sterile Manufacturing Operations" in risk.target_routing
    assert "ICH Q9" in risk.reasoning

def test_moderate_defect_evaluation():
    """Verify non-sterile packaging/closure defect evaluates to MEDIUM risk."""
    fields = {
        "product_name": "Metformin Hydrochloride",
        "product_grade_strength": "500mg Tablets",
        "complaint_type": "Packaging Defect",
        "complaint_description": "Bottles missing child-resistant closure seal.",
        "affected_quantity": 25
    }

    risk = RiskEngine.evaluate(fields=fields)
    assert risk.severity in ["MEDIUM", "HIGH"]
    assert risk.risk_score >= 12
    assert risk.requires_regulatory_escalation is False

def test_minor_cosmetic_defect():
    """Verify isolated outer carton cosmetic issue evaluates to LOW risk."""
    fields = {
        "product_name": "Ibuprofen",
        "product_grade_strength": "200mg",
        "complaint_type": "Secondary Packaging",
        "complaint_description": "Outer carton slightly creased during shipping.",
        "affected_quantity": 1
    }

    risk = RiskEngine.evaluate(fields=fields)
    assert risk.severity == "LOW"
    assert "P4" in risk.priority
    assert risk.risk_score < 12
    assert risk.requires_regulatory_escalation is False

def test_adverse_event_escalation():
    """Verify reported patient adverse event triggers CRITICAL and regulatory escalation."""
    fields = {
        "product_name": "Amoxicillin",
        "product_grade_strength": "250mg",
        "complaint_description": "Patient developed severe anaphylaxis and required hospitalization.",
        "affected_quantity": 1
    }

    risk = RiskEngine.evaluate(fields=fields)
    assert risk.severity == "CRITICAL"
    assert risk.requires_regulatory_escalation is True
    assert "Pharmacovigilance" in risk.target_routing

def test_empty_input_gracefulness():
    """Verify empty or missing data returns clean default without exception."""
    risk = RiskEngine.evaluate(complaint=None, fields=None)
    assert risk.severity == "Awaiting Assessment"
    assert risk.priority == "Pending Triage"
    assert risk.risk_score is None
