from typing import Dict, Any, List, Optional, Tuple
from app.models.complaint import ComplaintRecord, RiskAssessment, FieldDiff
from app.store.state_store import store
from app.services.risk_engine import RiskEngine

# Definitions of the 3 mandatory tools for LLM Function Calling schemas
TOOLS_SCHEMA = [
    {
        "name": "log_complaint",
        "description": "Parses a new natural-language customer complaint into structured pharmaceutical attributes and triggers an initial ICH Q9-informed risk assessment.",
        "parameters": {
            "type": "object",
            "properties": {
                "complaint_source": {"type": "string", "description": "Standardized source, e.g., 'Hospital / Healthcare Facility', 'Retail Pharmacy', 'Patient', 'Distributor'"},
                "customer_name": {"type": "string", "description": "Exact name of reporting customer or healthcare institution (e.g., 'St. Jude Memorial Hospital'). Avoid generic words like 'A hospital'."},
                "product_name": {"type": "string", "description": "Trade or generic pharmaceutical drug name (e.g., 'CardioSafe', 'Epinephrine Injection')"},
                "product_grade_strength": {"type": "string", "description": "Strength or grade exactly as stated in the text (e.g., '10 mg', '1 mg/mL'). Do not append unmentioned standards like USP if not stated."},
                "dosage_form": {"type": "string", "description": "Dosage form if stated (e.g., 'Immediate-release tablets', 'tablets', 'injection')"},
                "packaging": {"type": "string", "description": "Packaging type if stated (e.g., 'PVC-Alu blister', 'vial')"},
                "manufacturer": {"type": "string", "description": "Manufacturer name if stated (e.g., 'ApexPharma Laboratories')"},
                "batch_number": {"type": "string", "description": "Lot or batch code, e.g., CS240817, B24017"},
                "manufacturing_date": {"type": "string", "description": "Manufacturing date as stated in text (e.g., '17 August 2026', 'June 15, 2026'). Do not invent values."},
                "expiry_date": {"type": "string", "description": "Expiry date as stated in text (e.g., '16 August 2028', 'June 14, 2028'). Do not invent values."},
                "affected_quantity": {"type": "integer", "description": "Number of defective units reported"},
                "unit_of_measure": {"type": "string", "description": "e.g., Tablets, units, ampoules, vials, bottles"},
                "complaint_type": {"type": "string", "description": "Classification: Product Quality / Physical Defect, Container Closure Leakage, etc."},
                "complaint_date": {"type": "string", "description": "Date complaint was received or reported, e.g. '13 September 2026', 'September 12, 2026'"},
                "complaint_description": {"type": "string", "description": "The complete, full complaint description preserving all customer-reported defect narrative and details. Do not summarize or truncate."},
                "purchase_location": {"type": "string", "description": "Dispensing pharmacy or purchase location if mentioned (e.g., 'Cornerstone Pharmacy, Downtown')"},
                "rx_number": {"type": "string", "description": "Prescription number if mentioned (e.g., '9982415')"}
            },
            "required": ["complaint_description"]
        }
    },
    {
        "name": "edit_complaint",
        "description": "Applies a partial update to the active complaint. Strictly modifies only specified fields while preserving all unmentioned fields.",
        "parameters": {
            "type": "object",
            "properties": {
                "updated_fields": {
                    "type": "object",
                    "description": "Dictionary of key-value pairs representing ONLY the fields that the user requested to change.",
                    "properties": {
                        "complaint_source": {"type": "string"},
                        "customer_name": {"type": "string"},
                        "product_name": {"type": "string"},
                        "product_grade_strength": {"type": "string"},
                        "dosage_form": {"type": "string"},
                        "packaging": {"type": "string"},
                        "manufacturer": {"type": "string"},
                        "batch_number": {"type": "string"},
                        "manufacturing_date": {"type": "string"},
                        "expiry_date": {"type": "string"},
                        "affected_quantity": {"type": "integer"},
                        "unit_of_measure": {"type": "string"},
                        "complaint_type": {"type": "string"},
                        "complaint_date": {"type": "string"},
                        "complaint_description": {"type": "string"},
                        "purchase_location": {"type": "string"},
                        "rx_number": {"type": "string"}
                    }
                },
                "edit_rationale": {"type": "string", "description": "Reason for modification"}
            },
            "required": ["updated_fields"]
        }
    },
    {
        "name": "extract_from_document",
        "description": "Populates a structured complaint record from parsed document content and initiates an ICH Q9-informed risk assessment.",
        "parameters": {
            "type": "object",
            "properties": {
                "extracted_data": {
                    "type": "object",
                    "description": "Extracted pharmaceutical complaint fields from uploaded file or text",
                    "properties": {
                        "complaint_source": {"type": "string"},
                        "customer_name": {"type": "string"},
                        "product_name": {"type": "string"},
                        "product_grade_strength": {"type": "string"},
                        "dosage_form": {"type": "string"},
                        "packaging": {"type": "string"},
                        "manufacturer": {"type": "string"},
                        "batch_number": {"type": "string"},
                        "manufacturing_date": {"type": "string"},
                        "expiry_date": {"type": "string"},
                        "affected_quantity": {"type": "integer"},
                        "unit_of_measure": {"type": "string"},
                        "complaint_type": {"type": "string"},
                        "complaint_date": {"type": "string"},
                        "complaint_description": {"type": "string"},
                        "purchase_location": {"type": "string"},
                        "rx_number": {"type": "string"}
                    }
                },
                "document_summary": {"type": "string", "description": "Brief summary of document contents"}
            },
            "required": ["extracted_data"]
        }
    }
]

class ToolsService:
    """Concrete execution handlers for the 3 mandatory tools"""

    @staticmethod
    def execute_log_complaint(
        session_id: str,
        arguments: Dict[str, Any],
        user_prompt: str
    ) -> Tuple[ComplaintRecord, Dict[str, Any], List[str]]:
        """
        Tool 1 Handler: Creates a new complaint, executes ICH Q9 risk assessment,
        and returns the record with tool badges.
        """
        # Normalize standardized complaint_source, unit_of_measure, and purchase_location
        src = arguments.get("complaint_source")
        if src and src.lower() in ["hospital", "healthcare facility", "clinic", "hospital / clinic"]:
            arguments["complaint_source"] = "Hospital / Healthcare Facility"
        if arguments.get("unit_of_measure"):
            arguments["unit_of_measure"] = arguments["unit_of_measure"].capitalize()
        if arguments.get("purchase_location"):
            import re
            arguments["purchase_location"] = re.sub(r',\s*', ', ', arguments["purchase_location"].strip())

        record = store.create_or_replace_complaint(
            session_id=session_id,
            fields=arguments,
            user_prompt=user_prompt,
            trigger_source="log_complaint"
        )
        
        # Execute ICH Q9 risk assessment
        risk = RiskEngine.evaluate(complaint=record)
        record = store.update_risk_assessment(session_id=session_id, risk=risk)

        # Build field diffs for initial population highlight
        diffs = {}
        for k, v in arguments.items():
            if v is not None:
                diffs[k] = {"old": None, "new": v}

        badges = ["[✓ Log Complaint]", f"[✓ Risk Assessment: {risk.severity}]"]
        return record, diffs, badges

    @staticmethod
    def execute_edit_complaint(
        session_id: str,
        arguments: Dict[str, Any],
        user_prompt: str
    ) -> Tuple[ComplaintRecord, Dict[str, Any], List[str]]:
        """
        Tool 2 Handler: Applies partial delta, preserves all untouched fields,
        and conditionally recalculates risk if risk factors changed.
        """
        updated_fields = arguments.get("updated_fields", {})
        record, diffs, is_risk_impacted = store.apply_delta(
            session_id=session_id,
            updated_fields=updated_fields,
            user_prompt=user_prompt,
            trigger_source="edit_complaint"
        )

        badges = []
        for field, diff in diffs.items():
            badges.append(f"[✓ Updated {field}: {diff['old']} → {diff['new']}]")

        if is_risk_impacted:
            new_risk = RiskEngine.evaluate(complaint=record)
            record = store.update_risk_assessment(session_id=session_id, risk=new_risk)
            badges.append(f"[✓ Risk Recalculated: {new_risk.severity}]")

        return record, diffs, badges

    @staticmethod
    def execute_extract_from_document(
        session_id: str,
        arguments: Dict[str, Any],
        user_prompt: str = "Uploaded Document"
    ) -> Tuple[ComplaintRecord, Dict[str, Any], List[str]]:
        """
        Tool 3 Handler: Hydrates complaint state from extracted document attributes
        and executes initial ICH Q9 risk assessment.
        """
        extracted_data = arguments.get("extracted_data", {})
        summary = arguments.get("document_summary", "Document Extracted")
        
        # Normalize standardized complaint_source, unit_of_measure, and purchase_location
        src = extracted_data.get("complaint_source")
        if src and src.lower() in ["hospital", "healthcare facility", "clinic", "hospital / clinic"]:
            extracted_data["complaint_source"] = "Hospital / Healthcare Facility"
        if extracted_data.get("unit_of_measure"):
            extracted_data["unit_of_measure"] = extracted_data["unit_of_measure"].capitalize()
        if extracted_data.get("purchase_location"):
            import re
            extracted_data["purchase_location"] = re.sub(r',\s*', ', ', extracted_data["purchase_location"].strip())

        record = store.create_or_replace_complaint(
            session_id=session_id,
            fields=extracted_data,
            user_prompt=user_prompt,
            trigger_source="document_extraction"
        )

        risk = RiskEngine.evaluate(complaint=record)
        record = store.update_risk_assessment(session_id=session_id, risk=risk)

        diffs = {}
        for k, v in extracted_data.items():
            if v is not None:
                diffs[k] = {"old": None, "new": v}

        badges = [
            f"[✓ Document Extraction: {summary[:25]}]",
            f"[✓ Form Populated ({len(diffs)} fields)]",
            f"[✓ Risk Assessment: {risk.severity}]"
        ]
        return record, diffs, badges
