from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from app.models.complaint import (
    ComplaintRecord, 
    AuditEntry, 
    ProductDetails, 
    ManufacturingDetails, 
    ComplaintDetails, 
    RiskAssessment,
    get_utc_now
)

# Field-to-submodel mapping
FIELD_SECTION_MAP = {
    "complaint_source": "origin_customer",
    "customer_name": "origin_customer",
    "complaint_type": "origin_customer",
    "complaint_date": "origin_customer",
    "complaint_description": "origin_customer",
    "purchase_location": "origin_customer",
    "rx_number": "origin_customer",
    
    "product_name": "product_batch",
    "product_grade_strength": "product_batch",
    "dosage_form": "product_batch",
    "packaging": "product_batch",
    "manufacturer": "product_batch",
    
    "batch_number": "manufacturing",
    "manufacturing_date": "manufacturing",
    "expiry_date": "manufacturing",
    "affected_quantity": "manufacturing",
    "unit_of_measure": "manufacturing",
}

# Fields that trigger risk re-evaluation when modified
RISK_BEARING_FIELDS = {
    "affected_quantity",
    "complaint_type",
    "complaint_description",
    "product_name",
    "batch_number"
}

class ComplaintStore:
    """
    In-memory session store designed with auditability principles inspired by 21 CFR Part 11.
    Maintains active complaint state, applies partial updates (JSON merge patch),
    and appends immutable audit records with field deltas.
    """
    def __init__(self):
        self._sessions: Dict[str, ComplaintRecord] = {}

    def get_complaint(self, session_id: str = "default") -> Optional[ComplaintRecord]:
        return self._sessions.get(session_id)

    def get_or_create_complaint(self, session_id: str = "default") -> ComplaintRecord:
        if session_id not in self._sessions:
            self._sessions[session_id] = ComplaintRecord()
        return self._sessions[session_id]

    def create_or_replace_complaint(
        self,
        session_id: str = "default",
        fields: Optional[Dict[str, Any]] = None,
        user_prompt: Optional[str] = None,
        trigger_source: str = "log_complaint"
    ) -> ComplaintRecord:
        """
        Creates a new complaint record, populates initial fields, and logs creation audit.
        """
        record = ComplaintRecord()
        fields = fields or {}
        diffs: Dict[str, Dict[str, Any]] = {}

        for field_name, value in fields.items():
            section_name = FIELD_SECTION_MAP.get(field_name)
            if section_name:
                section_obj = getattr(record, section_name)
                if hasattr(section_obj, field_name):
                    old_val = getattr(section_obj, field_name)
                    if value != old_val:
                        setattr(section_obj, field_name, value)
                        diffs[field_name] = {"old": old_val, "new": value}

        audit_entry = AuditEntry(
            trigger_source=trigger_source,
            user_prompt=user_prompt,
            field_changes=diffs,
            risk_recalculated=True
        )
        record.audit_trail.append(audit_entry)
        record.updated_at = get_utc_now()
        
        self._sessions[session_id] = record
        return record

    def apply_delta(
        self,
        session_id: str = "default",
        updated_fields: Optional[Dict[str, Any]] = None,
        user_prompt: Optional[str] = None,
        trigger_source: str = "edit_complaint"
    ) -> Tuple[ComplaintRecord, Dict[str, Dict[str, Any]], bool]:
        """
        Applies a partial update to the active complaint record.
        Only fields specified in updated_fields are mutated; all other fields are preserved.
        Returns: (updated_record, field_diffs, is_risk_impacted)
        """
        record = self.get_or_create_complaint(session_id)
        updated_fields = updated_fields or {}
        diffs: Dict[str, Dict[str, Any]] = {}
        is_risk_impacted = False

        for field_name, value in updated_fields.items():
            section_name = FIELD_SECTION_MAP.get(field_name)
            if section_name:
                section_obj = getattr(record, section_name)
                if hasattr(section_obj, field_name):
                    old_val = getattr(section_obj, field_name)
                    if value != old_val:
                        setattr(section_obj, field_name, value)
                        diffs[field_name] = {"old": old_val, "new": value}
                        if field_name in RISK_BEARING_FIELDS:
                            is_risk_impacted = True

        if diffs:
            audit_entry = AuditEntry(
                trigger_source=trigger_source,
                user_prompt=user_prompt,
                field_changes=diffs,
                risk_recalculated=is_risk_impacted
            )
            record.audit_trail.append(audit_entry)
            record.updated_at = get_utc_now()

        return record, diffs, is_risk_impacted

    def update_risk_assessment(
        self,
        session_id: str = "default",
        risk: Optional[RiskAssessment] = None
    ) -> ComplaintRecord:
        """Attaches or updates the risk assessment on the active complaint record."""
        record = self.get_or_create_complaint(session_id)
        if risk:
            record.risk_assessment = risk
            record.status = "Under QA Review" if risk.severity in ["HIGH", "CRITICAL"] else "Pending Triage"
            record.updated_at = get_utc_now()
        return record

    def reset_session(self, session_id: str = "default") -> ComplaintRecord:
        """Resets the complaint state for the session to an empty record."""
        new_record = ComplaintRecord()
        self._sessions[session_id] = new_record
        return new_record

# Global singleton store
store = ComplaintStore()
