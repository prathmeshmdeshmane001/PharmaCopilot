from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid

def get_utc_now():
    return datetime.now(timezone.utc)

class FieldDiff(BaseModel):
    old: Any = None
    new: Any = None

class ProductDetails(BaseModel):
    product_name: Optional[str] = Field(default=None, description="Brand or generic name of the pharmaceutical product")
    product_grade_strength: Optional[str] = Field(default=None, description="Strength or pharmacopeial grade, e.g., 1mg/mL, 500mg, USP")
    dosage_form: Optional[str] = Field(default=None, description="Dosage form, e.g., Immediate-release tablets, capsules, injectable solution")
    packaging: Optional[str] = Field(default=None, description="Packaging type, e.g., PVC-Alu blister, HDPE bottle, glass vial")
    manufacturer: Optional[str] = Field(default=None, description="Manufacturing organization, e.g., ApexPharma Laboratories")

class ManufacturingDetails(BaseModel):
    batch_number: Optional[str] = Field(default=None, description="Lot or batch identifier, e.g., B24017")
    manufacturing_date: Optional[str] = Field(default=None, description="Manufacturing date in YYYY-MM-DD or standard date format")
    expiry_date: Optional[str] = Field(default=None, description="Expiry date in YYYY-MM-DD or standard date format")
    affected_quantity: Optional[int] = Field(default=None, description="Reported defective count")
    unit_of_measure: str = Field(default="units", description="Unit of measurement, e.g., units, vials, kg, bottles, tablets")

class ComplaintDetails(BaseModel):
    complaint_source: Optional[str] = Field(default=None, description="Source of complaint, e.g., Hospital, Pharmacy, Distributor, Patient")
    customer_name: Optional[str] = Field(default=None, description="Reporting customer or facility name")
    complaint_type: Optional[str] = Field(default=None, description="Defect classification, e.g., Packaging Defect, Particulate Matter, Container Leakage")
    complaint_date: Optional[str] = Field(default=None, description="Date complaint was received/reported")
    complaint_description: Optional[str] = Field(default=None, description="Detailed narrative of customer complaint")
    purchase_location: Optional[str] = Field(default=None, description="Point of sale or dispensing facility, e.g., Cornerstone Pharmacy, Downtown")
    rx_number: Optional[str] = Field(default=None, description="Prescription identifier if applicable, e.g., 9982415")

class RiskAssessment(BaseModel):
    severity: str = Field(default="Awaiting Assessment", description="Calculated severity: CRITICAL, HIGH, MEDIUM, LOW")
    priority: str = Field(default="Pending Triage", description="Triage priority: P1 - Immediate, P2 - Urgent, P3 - Standard, P4 - Minor")
    risk_score: Optional[int] = Field(default=None, description="Calculated quantitative Risk Priority Number (RPN: 1-125)")
    reasoning: Optional[str] = Field(default=None, description="Clinical and compliance rationale for the risk assessment")
    recommended_actions: List[str] = Field(default_factory=list, description="Prescribed immediate mitigation actions")
    target_routing: List[str] = Field(default_factory=list, description="Target departments for escalation and investigation")
    requires_regulatory_escalation: bool = Field(default=False, description="Flag indicating whether expedited QA/Regulatory review for potential authority notification is recommended")
    assessed_at: Optional[datetime] = Field(default=None, description="Timestamp when risk assessment was generated")

class AuditEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=get_utc_now)
    trigger_source: str = Field(default="ai_copilot", description="Trigger: log_complaint, edit_complaint, document_extraction")
    user_prompt: Optional[str] = Field(default=None, description="Natural language prompt that initiated the change")
    field_changes: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Dictionary of field deltas: {'field_name': {'old': old_val, 'new': new_val}}"
    )
    risk_recalculated: bool = Field(default=False, description="Whether this action triggered risk recalculation")

class ComplaintRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    complaint_number: str = Field(default_factory=lambda: f"CMP-2026-{uuid.uuid4().hex[:4].upper()}")
    status: str = Field(default="Pending Triage", description="Status: Draft, Pending Triage, Under QA Review, Escalated, Closed")
    origin_customer: ComplaintDetails = Field(default_factory=ComplaintDetails)
    product_batch: ProductDetails = Field(default_factory=ProductDetails)
    manufacturing: ManufacturingDetails = Field(default_factory=ManufacturingDetails)
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)
    audit_trail: List[AuditEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

class ComplaintDelta(BaseModel):
    """Payload representing partial field updates extracted from natural language or documents"""
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_grade_strength: Optional[str] = None
    dosage_form: Optional[str] = None
    packaging: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    affected_quantity: Optional[int] = None
    unit_of_measure: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    complaint_description: Optional[str] = None
    purchase_location: Optional[str] = None
    rx_number: Optional[str] = None
