from app.models.complaint import (
    ComplaintRecord,
    ProductDetails,
    ManufacturingDetails,
    ComplaintDetails,
    RiskAssessment,
    AuditEntry
)

def test_complaint_record_defaults():
    record = ComplaintRecord()
    assert record.id is not None
    assert record.complaint_number.startswith("CMP-2026-")
    assert record.status == "Pending Triage"
    assert record.origin_customer.complaint_source is None
    assert record.product_batch.product_name is None
    assert record.manufacturing.affected_quantity is None
    assert record.manufacturing.unit_of_measure == "units"
    assert record.risk_assessment.severity == "Awaiting Assessment"
    assert len(record.audit_trail) == 0

def test_complaint_record_serialization():
    record = ComplaintRecord(
        origin_customer=ComplaintDetails(
            customer_name="St. Jude Hospital",
            complaint_source="Hospital Pharmacovigilance",
            complaint_description="Leaking vials in Batch B24017"
        ),
        product_batch=ProductDetails(
            product_name="Epinephrine",
            product_grade_strength="1mg/mL"
        ),
        manufacturing=ManufacturingDetails(
            batch_number="B24017",
            affected_quantity=50
        ),
        risk_assessment=RiskAssessment(
            severity="HIGH",
            priority="P1 - Immediate",
            risk_score=16,
            reasoning="Sterility breach in injectable"
        )
    )

    data = record.model_dump()
    assert data["origin_customer"]["customer_name"] == "St. Jude Hospital"
    assert data["product_batch"]["product_name"] == "Epinephrine"
    assert data["manufacturing"]["batch_number"] == "B24017"
    assert data["manufacturing"]["affected_quantity"] == 50
    assert data["risk_assessment"]["severity"] == "HIGH"
