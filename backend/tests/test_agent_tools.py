import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.tools import ToolsService
from app.store.state_store import store

client = TestClient(app)

def test_tools_service_log_and_edit():
    session_id = "test-tools-1"
    store.reset_session(session_id)

    # 1. Test log_complaint
    log_args = {
        "product_name": "Epinephrine Injection",
        "product_grade_strength": "1 mg/mL, USP",
        "batch_number": "B24017",
        "affected_quantity": 50,
        "complaint_type": "Container Closure Leakage",
        "complaint_description": "Vials leaking around neck seal during unpacking."
    }
    record, diffs, badges = ToolsService.execute_log_complaint(
        session_id=session_id,
        arguments=log_args,
        user_prompt="Log complaint for Epinephrine B24017 50 units leaking"
    )

    assert record.product_batch.product_name == "Epinephrine Injection"
    assert record.manufacturing.batch_number == "B24017"
    assert record.manufacturing.affected_quantity == 50
    assert record.risk_assessment.severity == "CRITICAL"
    assert "[✓ Log Complaint]" in badges
    assert any("Risk Assessment" in b for b in badges)

    # 2. Test edit_complaint: Edit quantity from 50 to 75
    edit_args = {
        "updated_fields": {"affected_quantity": 75},
        "edit_rationale": "Customer updated quantity count"
    }
    updated_record, diffs, edit_badges = ToolsService.execute_edit_complaint(
        session_id=session_id,
        arguments=edit_args,
        user_prompt="Actually, the affected quantity is 75 units."
    )

    # Verify updated quantity
    assert updated_record.manufacturing.affected_quantity == 75
    assert "affected_quantity" in diffs
    assert diffs["affected_quantity"]["old"] == 50
    assert diffs["affected_quantity"]["new"] == 75

    # CRITICAL: Verify untouched fields remain strictly preserved!
    assert updated_record.product_batch.product_name == "Epinephrine Injection"
    assert updated_record.product_batch.product_grade_strength == "1 mg/mL, USP"
    assert updated_record.manufacturing.batch_number == "B24017"
    assert updated_record.origin_customer.complaint_type == "Container Closure Leakage"

    # Verify badges
    assert any("Updated affected_quantity" in b for b in edit_badges)

def test_api_chat_flow():
    """Integration test verifying end-to-end multi-turn conversation over /api/chat."""
    session_id = "test-chat-session"
    store.reset_session(session_id)

    # Turn 1: Log complaint via natural language
    res1 = client.post("/api/chat", json={
        "session_id": session_id,
        "message": "Received complaint for Epinephrine Injection, Batch B24017, 50 units leaking."
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert "[✓ Log Complaint]" in data1["tool_badges"]
    complaint1 = data1["complaint"]
    assert complaint1["product_batch"]["product_name"] == "Epinephrine Injection"
    assert complaint1["manufacturing"]["batch_number"] == "B24017"
    assert complaint1["manufacturing"]["affected_quantity"] == 50
    assert complaint1["risk_assessment"]["severity"] == "CRITICAL"

    # Turn 2: Natural-language edit modifying only quantity
    res2 = client.post("/api/chat", json={
        "session_id": session_id,
        "message": "Actually, the affected quantity is 75 units."
    })
    assert res2.status_code == 200
    data2 = res2.json()
    complaint2 = data2["complaint"]
    
    # Verify quantity modified
    assert complaint2["manufacturing"]["affected_quantity"] == 75
    # Verify other fields preserved
    assert complaint2["product_batch"]["product_name"] == "Epinephrine Injection"
    assert complaint2["manufacturing"]["batch_number"] == "B24017"
    assert any("Updated affected_quantity" in b for b in data2["tool_badges"])

    # Turn 3: Natural-language edit modifying batch number
    res3 = client.post("/api/chat", json={
        "session_id": session_id,
        "message": "Update batch number to B24099"
    })
    assert res3.status_code == 200
    data3 = res3.json()
    complaint3 = data3["complaint"]
    assert complaint3["manufacturing"]["batch_number"] == "B24099"
    assert complaint3["manufacturing"]["affected_quantity"] == 75  # Preserved from previous turn!
    assert complaint3["product_batch"]["product_name"] == "Epinephrine Injection"  # Preserved!

    # Check active complaint endpoint
    res_active = client.get(f"/api/complaints/active?session_id={session_id}")
    assert res_active.status_code == 200
    active_record = res_active.json()
    assert active_record["manufacturing"]["batch_number"] == "B24099"
    assert active_record["manufacturing"]["affected_quantity"] == 75
    assert len(active_record["audit_trail"]) == 3


def test_st_jude_hospital_complaint_extraction():
    """
    Test exact extraction and mapping of the St. Jude Memorial Hospital complaint:
    - customer name must be 'St. Jude Memorial Hospital'
    - manufacturing date 'June 15, 2026'
    - expiry date 'June 14, 2028'
    - complaint date 'September 12, 2026'
    - full complaint description preserved
    - product name 'Epinephrine Injection'
    - strength '1 mg/mL' (no unmentioned USP added)
    - batch 'B24017'
    - affected quantity 50
    - risk assessment severity CRITICAL / P1 with sterile guardrail
    """
    session_id = "test-st-jude-session"
    store.reset_session(session_id)

    prompt = (
        "A hospital has reported that 50 units of Epinephrine Injection 1 mg/mL from batch B24017 "
        "have leaking ampoules. The complaint was received from St. Jude Memorial Hospital on September 12, 2026. "
        "The affected product was manufactured on June 15, 2026 and expires on June 14, 2028. "
        "The customer reports that the ampoules have visible leakage and some packaging seals appear damaged. "
        "Please log this complaint, assess the risk, and recommend the appropriate action and routing."
    )

    response = client.post("/api/chat", json={"message": prompt, "session_id": session_id})
    assert response.status_code == 200, f"Chat call failed: {response.text}"
    data = response.json()
    complaint = data["complaint"]

    # 1. Customer Name
    assert complaint["origin_customer"]["customer_name"] == "St. Jude Memorial Hospital", \
        f"Customer name mismatch: {complaint['origin_customer']['customer_name']}"

    # 2. Manufacturing Date
    mfg_date = complaint["manufacturing"]["manufacturing_date"]
    assert mfg_date in ["June 15, 2026", "2026-06-15"], f"Unexpected mfg date: {mfg_date}"

    # 3. Expiry Date
    exp_date = complaint["manufacturing"]["expiry_date"]
    assert exp_date in ["June 14, 2028", "2028-06-14"], f"Unexpected expiry date: {exp_date}"

    # 4. Complaint Date
    cmp_date = complaint["origin_customer"]["complaint_date"]
    assert cmp_date in ["September 12, 2026", "2026-09-12"], f"Unexpected complaint date: {cmp_date}"

    # 5. Product & Batch
    assert complaint["product_batch"]["product_name"] == "Epinephrine Injection"
    assert complaint["product_batch"]["product_grade_strength"] == "1 mg/mL"
    assert complaint["manufacturing"]["batch_number"] == "B24017"
    assert complaint["manufacturing"]["affected_quantity"] == 50

    # 6. Full complaint description preserved
    desc = complaint["origin_customer"]["complaint_description"]
    assert desc is not None
    assert "leakage" in desc.lower() or "leaking" in desc.lower()
    assert "damaged" in desc.lower() or "seals" in desc.lower()

    # 7. Risk Assessment & Routing
    risk = complaint["risk_assessment"]
    assert risk["severity"] == "CRITICAL"
    assert "P1" in risk["priority"]
    assert risk["requires_regulatory_escalation"] is True
    assert len(risk["recommended_actions"]) > 0
    assert len(risk["target_routing"]) > 0

