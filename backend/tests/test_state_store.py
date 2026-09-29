from app.store.state_store import ComplaintStore

def test_store_creation_and_preservation():
    store = ComplaintStore()
    session_id = "test-session-1"

    # 1. Create initial complaint
    initial_data = {
        "product_name": "Epinephrine Injection",
        "product_grade_strength": "1mg/mL, USP",
        "batch_number": "B24017",
        "affected_quantity": 50,
        "complaint_description": "Vials leaking around crimp seal."
    }
    record = store.create_or_replace_complaint(
        session_id=session_id,
        fields=initial_data,
        user_prompt="Log complaint for Epinephrine batch B24017, 50 units leaking"
    )

    assert record.product_batch.product_name == "Epinephrine Injection"
    assert record.manufacturing.batch_number == "B24017"
    assert record.manufacturing.affected_quantity == 50
    assert len(record.audit_trail) == 1
    assert "affected_quantity" in record.audit_trail[0].field_changes

    # 2. Apply partial delta: Update ONLY affected_quantity to 75
    delta = {"affected_quantity": 75}
    updated_record, diffs, is_risk_impacted = store.apply_delta(
        session_id=session_id,
        updated_fields=delta,
        user_prompt="Actually, the affected quantity is 75 units."
    )

    # Verify updated field
    assert updated_record.manufacturing.affected_quantity == 75
    assert is_risk_impacted is True
    assert "affected_quantity" in diffs
    assert diffs["affected_quantity"]["old"] == 50
    assert diffs["affected_quantity"]["new"] == 75

    # CRITICAL: Verify untouched fields remain strictly preserved!
    assert updated_record.product_batch.product_name == "Epinephrine Injection"
    assert updated_record.product_batch.product_grade_strength == "1mg/mL, USP"
    assert updated_record.manufacturing.batch_number == "B24017"
    assert updated_record.origin_customer.complaint_description == "Vials leaking around crimp seal."

    # Verify audit trail appended
    assert len(updated_record.audit_trail) == 2
    assert updated_record.audit_trail[1].trigger_source == "edit_complaint"
    assert updated_record.audit_trail[1].field_changes["affected_quantity"]["new"] == 75

def test_store_non_risk_edit():
    store = ComplaintStore()
    session_id = "test-session-2"

    store.create_or_replace_complaint(
        session_id=session_id,
        fields={"customer_name": "General Clinic", "batch_number": "B100"}
    )

    # Edit customer name (not a risk-bearing field)
    record, diffs, is_risk_impacted = store.apply_delta(
        session_id=session_id,
        updated_fields={"customer_name": "St. Mary Medical Center"},
        user_prompt="Update customer name to St. Mary Medical Center"
    )

    assert record.origin_customer.customer_name == "St. Mary Medical Center"
    assert record.manufacturing.batch_number == "B100"  # Preserved
    assert is_risk_impacted is False  # Non-risk field modification

def test_api_reset_endpoint_clears_state():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.store.state_store import store

    client = TestClient(app)
    session_id = "test-reset-session"

    # Populate session with active complaint
    store.create_or_replace_complaint(
        session_id=session_id,
        fields={
            "product_name": "CardioSafe",
            "batch_number": "CS240817",
            "affected_quantity": 25,
            "complaint_description": "Damaged blister tablets"
        }
    )

    # Verify session has active fields
    active = store.get_complaint(session_id)
    assert active.product_batch.product_name == "CardioSafe"

    # Call reset endpoint
    res = client.post("/api/complaints/reset", json={"session_id": session_id})
    assert res.status_code == 200
    fresh = res.json()

    # Verify completely cleared initial state
    assert fresh["product_batch"]["product_name"] is None
    assert fresh["manufacturing"]["batch_number"] is None
    assert fresh["manufacturing"]["affected_quantity"] is None
    assert fresh["origin_customer"]["complaint_description"] is None
    assert fresh["audit_trail"] == []
    assert fresh["status"] == "Pending Triage"
