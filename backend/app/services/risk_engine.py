from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.complaint import ComplaintRecord, RiskAssessment, get_utc_now

# Keywords for pharmaceutical defect detection
STERILE_KEYWORDS = {
    "injection", "injectable", "vial", "ampoule", "infusion", "syringe", 
    "iv", "ophthalmic", "sterile", "intravenous", "intramuscular"
}

CRITICAL_DEFECT_KEYWORDS = {
    "leak", "leakage", "particulate", "speck", "contamination", "microbial", 
    "glass", "crack", "foreign matter", "anaphylaxis", "adverse event", 
    "hospitalization", "toxic", "death", "unsterile", "sterility", "precipitate"
}

MODERATE_DEFECT_KEYWORDS = {
    "cap", "seal", "sub-potency", "discoloration", "clumping", "tablets chipped", 
    "dissolution", "fill volume", "blister", "empty blister"
}

class RiskEngine:
    """
    ICH Q9–informed risk assessment engine.
    Calculates quantitative Risk Priority Number (RPN = Severity x Probability x Detectability),
    enforces pharmaceutical safety guardrails (e.g. sterile breach overrides),
    and generates explainable reasoning, recommended actions, and routing.
    """

    @classmethod
    def evaluate(
        cls, 
        complaint: Optional[ComplaintRecord] = None, 
        fields: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        # Extract relevant fields
        if complaint:
            product = (complaint.product_batch.product_name or "").lower()
            grade = (complaint.product_batch.product_grade_strength or "").lower()
            defect_type = (complaint.origin_customer.complaint_type or "").lower()
            desc = (complaint.origin_customer.complaint_description or "").lower()
            qty = complaint.manufacturing.affected_quantity or 0
        elif fields:
            product = str(fields.get("product_name") or "").lower()
            grade = str(fields.get("product_grade_strength") or "").lower()
            defect_type = str(fields.get("complaint_type") or "").lower()
            desc = str(fields.get("complaint_description") or "").lower()
            try:
                qty = int(fields.get("affected_quantity") or 0)
            except (ValueError, TypeError):
                qty = 0
        else:
            return RiskAssessment(
                severity="Awaiting Assessment",
                priority="Pending Triage",
                risk_score=None,
                reasoning="Insufficient data to compute risk assessment.",
                recommended_actions=["Gather product, batch, and defect details from customer."],
                target_routing=["Quality Assurance Triage"],
                assessed_at=get_utc_now()
            )

        full_context = f"{product} {grade} {defect_type} {desc}"

        # 1. Base Factor Evaluation: Severity (S: 1-5)
        is_sterile = any(k in full_context for k in STERILE_KEYWORDS)
        has_critical_defect = any(k in full_context for k in CRITICAL_DEFECT_KEYWORDS)
        has_moderate_defect = any(k in full_context for k in MODERATE_DEFECT_KEYWORDS)
        has_adverse_event = any(k in full_context for k in ["adverse", "reaction", "anaphylaxis", "hospital", "patient", "injury", "illness"])

        if has_critical_defect:
            severity_score = 5 if is_sterile or has_adverse_event else 4
        elif has_moderate_defect:
            severity_score = 3
        else:
            severity_score = 2

        # 2. Base Factor Evaluation: Probability of Recurrence (P: 1-5)
        if qty >= 500:
            probability_score = 4
        elif qty >= 50:
            probability_score = 3
        elif qty > 1:
            probability_score = 2
        else:
            probability_score = 1

        # 3. Base Factor Evaluation: Detectability (D: 1-5)
        # Higher score = harder to detect before patient administration
        if "particulate" in full_context or "sub-potency" in full_context or "contamination" in full_context:
            detectability_score = 4
        elif "leak" in full_context or "crack" in full_context:
            detectability_score = 3
        else:
            detectability_score = 2

        # Calculate base RPN
        rpn = severity_score * probability_score * detectability_score

        # 4. Pharmaceutical Safety Guardrail: Sterile Product Override
        sterile_breach_triggered = is_sterile and has_critical_defect

        if sterile_breach_triggered:
            severity_level = "CRITICAL"
            priority_level = "P1 - Immediate Action Required"
            rpn = max(rpn, 60)  # Clamp to CRITICAL threshold
            reasoning = (
                "Sterility breach identified in an injectable/sterile dosage form. "
                "Loss of container closure integrity or foreign particulate carries severe microbiological "
                "contamination hazards. Evaluated under ICH Q9 Quality Risk Management principles."
            )
            actions = [
                "Recommend QA review for potential batch quarantine across distribution inventory.",
                "Recommend initiating reserve sample sterility and endotoxin testing for QA evaluation.",
                "Recommend engineering audit of packaging line crimping and visual inspection controls.",
                "Recommend notifying Qualified Person (QP) and Head of Quality for triage review.",
                "Recommend QA and Regulatory Affairs evaluate need for field safety notification or market recall."
            ]
            routing = ["Quality Assurance", "Sterile Manufacturing Operations", "Regulatory Affairs"]
            requires_escalation = True

        elif rpn >= 60 or has_adverse_event:
            severity_level = "CRITICAL"
            priority_level = "P1 - Immediate Action Required"
            reasoning = (
                "Critical risk score or reported adverse event. High potential impact on patient health "
                "and regulatory compliance under ICH Q9 principles."
            )
            actions = [
                "Recommend QA review for potential batch quarantine pending investigation.",
                "Recommend convening Quality Review Board (QRB) for cross-functional evaluation.",
                "Recommend QA and Pharmacovigilance review for formal deviation and regulatory reporting assessment."
            ]
            routing = ["Quality Assurance", "Pharmacovigilance", "Regulatory Affairs"]
            requires_escalation = True

        elif rpn >= 30:
            severity_level = "HIGH"
            priority_level = "P2 - Urgent QA Investigation"
            reasoning = (
                "High risk defect with potential therapeutic or compliance impact. "
                "Multiple units affected; requires expedited root cause investigation under ICH Q9."
            )
            actions = [
                "Recommend QA evaluation of quality hold for affected batch pending investigation.",
                "Recommend QA inspect retained samples from the same packaging campaign.",
                "Recommend QC analytical check on defect root cause."
            ]
            routing = ["Quality Assurance", "Quality Control Analytical", "Packaging Engineering"]
            requires_escalation = False

        elif rpn >= 12:
            severity_level = "MEDIUM"
            priority_level = "P3 - Standard Evaluation"
            reasoning = (
                "Moderate quality defect with localized impact. "
                "No direct compromise to drug sterility or patient safety under ICH Q9 evaluation."
            )
            actions = [
                "Recommend QA inspection of packaging retain samples for trend confirmation.",
                "Recommend issuing replacement product to customer in accordance with SOP.",
                "Recommend logging in periodic quality trend review."
            ]
            routing = ["Quality Assurance", "Customer Support QA"]
            requires_escalation = False

        else:
            severity_level = "LOW"
            priority_level = "P4 - Trend Monitoring"
            reasoning = (
                "Minor cosmetic or isolated defect with negligible patient safety impact. "
                "Standard batch monitoring applies under ICH Q9."
            )
            actions = [
                "Recommend logging complaint in quality database for APQR (Annual Product Quality Review) trending.",
                "Recommend sending replacement unit to customer per standard procedure."
            ]
            routing = ["Quality Assurance Triage"]
            requires_escalation = False

        return RiskAssessment(
            severity=severity_level,
            priority=priority_level,
            risk_score=rpn,
            reasoning=reasoning,
            recommended_actions=actions,
            target_routing=routing,
            requires_regulatory_escalation=requires_escalation,
            assessed_at=get_utc_now()
        )
