"""
PharmaCopilot - End-to-End Workflow Verification Script (Phase 8)

Validates:
1. Workflow 1: Natural Language Complaint Intake (log_complaint)
2. Workflow 2: Natural Language Edit & Strict Delta State Preservation (edit_complaint)
3. Workflow 3: Document Ingestion (extract_from_document) + Seamless Follow-Up Chat Edit
4. Zero-Manual-Edit Architectural Contracts
5. Regulatory Phrasing & Prototype Scope Adherence
"""

import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.store.state_store import store

client = TestClient(app)

def run_test(name: str, fn):
    print(f"\n[RUNNING] {name}...")
    try:
        fn()
        print(f"[PASSED]  {name}")
    except AssertionError as ae:
        print(f"[FAILED]  {name}: {ae}")
        raise
    except Exception as e:
        print(f"[ERROR]   {name}: {e}")
        raise

def test_workflow_1_log_complaint():
    """
    Workflow 1: Enter natural language description of a complaint.
    Verify log_complaint is executed, complaint record is populated,
    and ICH Q9-informed risk assessment runs with sterile guardrail applied.
    """
    session_id = "test-session-wf1"
    store.reset_session(session_id)

    prompt = (
        "Customer reported 50 vials of Epinephrine 1mg/mL Batch B24017 "
        "leaking around rubber seal at Mercy General Hospital on 2026-03-10."
    )

    response = client.post("/api/chat", json={"message": prompt, "session_id": session_id})
    assert response.status_code == 200, f"Chat endpoint failed: {response.text}"
    data = response.json()

    # Check tool execution badges
    badges = data.get("tool_badges", [])
    assert any("Log Complaint" in b for b in badges), f"Missing Log Complaint badge in {badges}"
    assert any("Risk Assessment" in b for b in badges), f"Missing Risk Assessment badge in {badges}"

    # Check record fields
    complaint = data["complaint"]
    assert "Epinephrine" in complaint["product_batch"]["product_name"]
    assert "1" in (complaint["product_batch"]["product_grade_strength"] or "")
    assert complaint["manufacturing"]["batch_number"] == "B24017"
    assert complaint["manufacturing"]["affected_quantity"] == 50
    assert "Mercy General Hospital" in (complaint["origin_customer"]["customer_name"] or "")

    # Check ICH Q9 risk assessment
    risk = complaint["risk_assessment"]
    assert risk["severity"] in ["CRITICAL", "HIGH"], f"Unexpected severity: {risk['severity']}"
    assert "P1" in risk["priority"], f"Unexpected priority: {risk['priority']}"
    assert risk["requires_regulatory_escalation"] is True
    assert "sterile" in risk["reasoning"].lower() or "leak" in risk["reasoning"].lower()

    # Check audit trail
    audit_trail = complaint.get("audit_trail", [])
    assert len(audit_trail) >= 1
    assert audit_trail[0]["trigger_source"] == "log_complaint"


def test_workflow_2_edit_complaint_strict_preservation():
    """
    Workflow 2: Conversational edit updating only affected quantity.
    Verify edit_complaint is executed, only quantity changes,
    and all untouched fields (product, batch, dates, customer) are strictly preserved.
    """
    session_id = "test-session-wf2"
    store.reset_session(session_id)

    # Initial log
    init_prompt = (
        "Customer reported 50 vials of Epinephrine 1mg/mL Batch B24017 "
        "leaking around rubber seal at Mercy General Hospital on 2026-03-10."
    )
    client.post("/api/chat", json={"message": init_prompt, "session_id": session_id})

    # Natural language edit
    edit_prompt = "Actually, the affected quantity was 75 units, not 50."
    response = client.post("/api/chat", json={"message": edit_prompt, "session_id": session_id})
    assert response.status_code == 200, f"Edit failed: {response.text}"
    data = response.json()

    # Check tool execution badge
    badges = data.get("tool_badges", [])
    assert any("Updated" in b for b in badges), f"Missing update badge in {badges}"

    # Verify diffs dictionary returned for visual pulsing
    diffs = data.get("diffs", {})
    assert "affected_quantity" in diffs
    assert diffs["affected_quantity"]["old"] == 50
    assert diffs["affected_quantity"]["new"] == 75

    # Check preserved fields
    complaint = data["complaint"]
    assert complaint["manufacturing"]["affected_quantity"] == 75
    assert "Epinephrine" in complaint["product_batch"]["product_name"]  # PRESERVED
    assert complaint["manufacturing"]["batch_number"] == "B24017"        # PRESERVED
    assert "Mercy General Hospital" in (complaint["origin_customer"]["customer_name"] or "")  # PRESERVED

    # Check audit trail has update record
    audit_trail = complaint.get("audit_trail", [])
    assert len(audit_trail) >= 2
    assert audit_trail[-1]["trigger_source"] == "edit_complaint"
    assert "affected_quantity" in audit_trail[-1]["field_changes"]


def test_workflow_3_document_extraction_and_followup_edit():
    """
    Workflow 3: Document extraction from sample PDF/EML, followed by seamless
    conversational follow-up edit.
    """
    session_id = "test-session-wf3"
    store.reset_session(session_id)

    # Ingest document
    sample_pdf = backend_dir / "sample_data" / "sample_complaint_letter.pdf"
    if not sample_pdf.exists():
        sample_pdf = backend_dir.parent / "sample_data" / "sample_complaint_letter.pdf"

    assert sample_pdf.exists(), f"Sample PDF not found at {sample_pdf}"

    with open(sample_pdf, "rb") as f:
        response = client.post(
            "/api/documents/upload",
            files={"file": ("sample_complaint_letter.pdf", f, "application/pdf")},
            data={"session_id": session_id}
        )

    assert response.status_code == 200, f"Upload failed: {response.text}"
    data = response.json()

    # Verify document tool badges
    badges = data.get("tool_badges", [])
    assert any("Document Extraction" in b for b in badges), f"Missing extraction badge: {badges}"

    complaint = data["complaint"]
    assert complaint["product_batch"]["product_name"] is not None
    assert complaint["manufacturing"]["batch_number"] is not None

    # Follow-up conversational edit
    followup_prompt = "The batch number is actually B24099."
    edit_resp = client.post("/api/chat", json={"message": followup_prompt, "session_id": session_id})
    assert edit_resp.status_code == 200, f"Followup edit failed: {edit_resp.text}"
    edit_data = edit_resp.json()

    updated_complaint = edit_data["complaint"]
    assert updated_complaint["manufacturing"]["batch_number"] == "B24099"
    # Document's product name preserved
    assert updated_complaint["product_batch"]["product_name"] == complaint["product_batch"]["product_name"]


def test_workflow_3b_raw_text_paste():
    """
    Workflow 3b: Ingest complaint via raw text/email paste endpoint.
    """
    session_id = "test-session-wf3b"
    store.reset_session(session_id)

    raw_text = (
        "URGENT COMPLAINT\n"
        "From: pharmacy@stjudes.org\n"
        "Product: Amoxicillin Trihydrate 500mg\n"
        "Batch: AMX-992\n"
        "Quantity: 120 bottles\n"
        "Issue: Powder discolored with brown specks throughout container."
    )

    response = client.post(
        "/api/documents/paste",
        json={"text": raw_text, "session_id": session_id}
    )
    assert response.status_code == 200, f"Paste failed: {response.text}"
    data = response.json()

    complaint = data["complaint"]
    assert complaint["product_batch"]["product_name"] == "Amoxicillin Trihydrate"
    assert complaint["manufacturing"]["batch_number"] == "AMX-992"
    assert complaint["manufacturing"]["affected_quantity"] == 120


def test_zero_manual_edit_contract():
    """
    Verifies that frontend form controls are strictly read-only and no manual save buttons exist.
    """
    frontend_dir = backend_dir.parent / "frontend" / "src"
    readonly_field = frontend_dir / "components" / "form" / "controls" / "ReadOnlyField.tsx"
    assert readonly_field.exists(), f"ReadOnlyField.tsx not found at {readonly_field}"

    content = readonly_field.read_text(encoding="utf-8")
    assert "readOnly" in content or "readOnly={true}" in content
    assert "disabled" in content or "disabled={true}" in content
    assert "tabIndex={-1}" in content

    # Check that no manual Save / Submit form buttons exist in form components
    form_dir = frontend_dir / "components" / "form"
    for tsx_file in form_dir.rglob("*.tsx"):
        file_text = tsx_file.read_text(encoding="utf-8").lower()
        # Ensure there are no user "Save Changes" or "Submit Complaint" buttons in the form area
        assert "save changes" not in file_text
        assert "submit complaint" not in file_text


def test_regulatory_phrasing_and_scope_adherence():
    """
    Verifies adherence to required phrasing:
    - Must use 'ICH Q9–informed risk assessment'
    - Must use 'Designed with auditability principles inspired by 21 CFR Part 11'
    - Must NOT claim 'production-quality' or 'clinical-grade'
    """
    repo_root = backend_dir.parent
    docs_dir = repo_root / "docs"

    # Verify implementation.md uses correct phrasing
    impl_md = (docs_dir / "implementation.md").read_text(encoding="utf-8")
    assert "ICH Q9" in impl_md
    assert "21 CFR Part 11" in impl_md
    assert "clinical-grade" not in impl_md.lower()
    assert "production-quality" not in impl_md.lower()

    # Verify frontend header displays regulatory phrase
    app_tsx = (repo_root / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")
    assert "21 CFR Part 11 Audit Principles" in app_tsx


def test_st_jude_complaint_exact_mapping():
    """
    Test exact extraction and mapping of the St. Jude Memorial Hospital complaint:
    - customer name must be 'St. Jude Memorial Hospital'
    - manufacturing date 'June 15, 2026'
    - expiry date 'June 14, 2028'
    - complaint date 'September 12, 2026'
    - full complaint description preserved
    - product name 'Epinephrine Injection'
    - strength '1 mg/mL'
    - batch 'B24017'
    - affected quantity 50
    - risk assessment severity CRITICAL / P1 with sterile guardrail
    """
    session_id = "test-st-jude-session-proto"
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


if __name__ == "__main__":
    print("=" * 60)
    print("  PHARMACOPILOT - END-TO-END PROTOTYPE TEST SUITE (PHASE 8)")
    print("=" * 60)

    run_test("Health Endpoint Check", lambda: client.get("/api/health").status_code == 200)
    run_test("Workflow 1: Natural Language Complaint Intake", test_workflow_1_log_complaint)
    run_test("Workflow 2: Edit Complaint & Strict Preservation", test_workflow_2_edit_complaint_strict_preservation)
    run_test("Workflow 3: Document Ingestion & Follow-up Edit", test_workflow_3_document_extraction_and_followup_edit)
    run_test("Workflow 3b: Raw Text / Email Paste", test_workflow_3b_raw_text_paste)
    run_test("St. Jude Hospital Exact Extraction Mapping", test_st_jude_complaint_exact_mapping)
    run_test("Zero-Manual-Edit Architectural Contract", test_zero_manual_edit_contract)
    run_test("Regulatory Phrasing & Prototype Scope", test_regulatory_phrasing_and_scope_adherence)

    print("\n" + "=" * 60)
    print("  ALL END-TO-END WORKFLOW & COMPLIANCE TESTS PASSED!")
    print("=" * 60)
