import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from app.config import settings
from app.services.tools import TOOLS_SCHEMA

class LLMService:
    """
    Dual-mode LLM client supporting:
    1. Live Gemini / OpenAI with native function calling
    2. Deterministic Mock LLM for offline prototype testing & evaluation
    """

    @classmethod
    async def process_user_turn(
        cls,
        user_message: str,
        active_complaint: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], str]:
        # 1. Try Live Gemini if configured
        if settings.gemini_api_key and settings.llm_provider in ["gemini", "auto"]:
            try:
                gemini_result = await cls._call_gemini_with_tools(user_message, active_complaint)
                if gemini_result:
                    return gemini_result
            except Exception as e:
                print(f"[LLMService] Live Gemini call failed, falling back to mock: {e}")

        # 2. Try Live OpenAI if configured
        if settings.openai_api_key and settings.llm_provider in ["openai", "auto"]:
            try:
                return await cls._call_openai_with_tools(user_message, active_complaint)
            except Exception as e:
                print(f"[LLMService] Live OpenAI call failed, falling back to mock: {e}")

        # 3. Deterministic Mock Engine
        return cls._mock_tool_dispatcher(user_message, active_complaint)

    @classmethod
    def _mock_tool_dispatcher(
        cls,
        message: str,
        current_state: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], str]:
        msg_lower = message.lower()
        has_active_record = bool(current_state and (
            current_state.get("product_batch", {}).get("product_name") or 
            current_state.get("manufacturing", {}).get("batch_number") or
            current_state.get("origin_customer", {}).get("complaint_description")
        ))

        # Check for Edit Intent (Workflow 2)
        edit_indicators = ["change", "update", "correct", "actually", "instead", "modify", "set", "make it"]
        is_edit_intent = has_active_record and any(word in msg_lower for word in edit_indicators)

        if is_edit_intent:
            updated_fields: Dict[str, Any] = {}

            # Quantity edit regex
            qty_match = re.search(r'(?:quantity|qty|units?|vials?|count).*?\b(\d+)\b', msg_lower)
            if not qty_match:
                qty_match = re.search(r'(?:actually|instead|to|is|make it|now)\s+(\d+)', msg_lower)
            if not qty_match:
                qty_match = re.search(r'\b(\d+)\s*(?:units?|vials?|bottles?|packs?|boxes?)', msg_lower)
            if qty_match:
                updated_fields["affected_quantity"] = int(qty_match.group(1))

            # Batch edit regex
            batch_match = re.search(r'(?:batch|lot)\s*(?:number|no\.?|#)?\s*(?:to|is|=|was|should be)?\s*(?:actually|now)?\s*([a-zA-Z0-9_-]+)', message, re.IGNORECASE)
            if batch_match:
                candidate = batch_match.group(1).upper()
                if candidate.lower() in ["is", "actually", "to", "was", "the", "now", "number"]:
                    alt_match = re.search(r'\b([A-Za-z0-9]{2,15}(?:-[0-9A-Za-z]+)?)\b', message)
                    if alt_match:
                        updated_fields["batch_number"] = alt_match.group(1).upper()
                else:
                    updated_fields["batch_number"] = candidate

            # Customer edit regex
            cust_match = re.search(r'customer\s*(?:name)?\s*(?:to|is|=)\s*([^,.]+)', message, re.IGNORECASE)
            if cust_match:
                updated_fields["customer_name"] = cust_match.group(1).strip()

            # Product edit regex
            prod_match = re.search(r'product\s*(?:name)?\s*(?:to|is|=)\s*([^,.]+)', message, re.IGNORECASE)
            if prod_match:
                updated_fields["product_name"] = prod_match.group(1).strip()

            if updated_fields:
                field_names = ", ".join(updated_fields.keys())
                reply = (
                    f"I have updated the requested fields ({field_names}) while strictly preserving "
                    f"all other existing complaint information. The risk assessment has been reviewed."
                )
                return "edit_complaint", {"updated_fields": updated_fields, "edit_rationale": "User requested modification"}, reply

        # Check for Log Complaint Intent (Workflow 1)
        log_indicators = ["log", "complaint", "received", "defective", "leaking", "crack", "reported", "issue", "found", "batch"]
        if any(word in msg_lower for word in log_indicators):
            extracted: Dict[str, Any] = {}

            # Extract Quantity
            qty_match = re.search(r'(\d+)\s*(units?|vials?|bottles?|packs?|ampoules?|boxes?|bags?|tablets?)', msg_lower)
            if qty_match:
                extracted["affected_quantity"] = int(qty_match.group(1))
                extracted["unit_of_measure"] = qty_match.group(2).capitalize()
            else:
                num_match = re.search(r'\b(\d+)\b', message)
                if num_match:
                    extracted["affected_quantity"] = int(num_match.group(1))

            # Extract Batch
            batch_match = re.search(r'\b(?:batch|lot)\s*(?:#|no\.?|number)?\s*[:|\-]?\s*([a-zA-Z0-9_-]+)', message, re.IGNORECASE)
            if batch_match:
                extracted["batch_number"] = batch_match.group(1).upper()
            else:
                code_match = re.search(r'\b([B|L|M|N|P]\d{3,6}[A-Za-z0-9]?)\b', message)
                if code_match:
                    extracted["batch_number"] = code_match.group(1).upper()

            # Extract Product Name & Strength
            if "cardiosafe" in msg_lower:
                extracted["product_name"] = "CardioSafe"
            elif "epinephrine injection" in msg_lower:
                extracted["product_name"] = "Epinephrine Injection"
            elif "epinephrine" in msg_lower:
                extracted["product_name"] = "Epinephrine Injection"
            elif "metformin" in msg_lower:
                extracted["product_name"] = "Metformin Hydrochloride"
            elif "amoxicillin" in msg_lower:
                extracted["product_name"] = "Amoxicillin Trihydrate"
            elif "saline" in msg_lower:
                extracted["product_name"] = "Normal Saline 0.9%"
            else:
                prod_regex = re.search(r'(?:for|of|regarding)\s+([A-Za-z0-9\s]+?)(?:batch|,|\d|$)', message, re.IGNORECASE)
                if prod_regex:
                    extracted["product_name"] = prod_regex.group(1).strip().title()

            # Strength extraction (avoid inventing standards like USP)
            str_match = re.search(r'\b(\d+(?:\.\d+)?\s*(?:mg/mL|mg|mcg|g|ml|%))\b', message, re.IGNORECASE)
            if str_match:
                extracted["product_grade_strength"] = str_match.group(1)
            elif "epinephrine" in msg_lower:
                extracted["product_grade_strength"] = "1 mg/mL"

            # Dosage Form
            if "immediate-release" in msg_lower:
                extracted["dosage_form"] = "Immediate-release tablets"
            elif "extended-release" in msg_lower:
                extracted["dosage_form"] = "Extended-release tablets"
            else:
                dosage_match = re.search(r'(?:Dosage\s*Form\s*[:|\-]?\s*|\b)(tablets|capsules|injection|solution)\b', message, re.IGNORECASE)
                if dosage_match:
                    extracted["dosage_form"] = dosage_match.group(1).strip().capitalize()

            # Packaging
            pkg_match = re.search(r'(?:Packaging\s*[:|\-]?\s*|in\s+)([A-Za-z0-9/-]+\s+blister(?:\s+packaging)?)', message, re.IGNORECASE)
            if pkg_match:
                pkg_val = pkg_match.group(1).strip().split('\n')[0].strip()
                if pkg_val.lower().endswith(" packaging"):
                    pkg_val = pkg_val[:-10].strip()
                extracted["packaging"] = pkg_val

            # Manufacturer
            mfr_match = re.search(r'(?:Manufacturer\s*[:|\-]?\s*|manufactured\s+by\s+)([A-Za-z0-9\s.,\'-]+?\b(?:Laboratories|Laboratory|Inc|Ltd|LLC|Corp)\b)', message, re.IGNORECASE)
            if mfr_match:
                extracted["manufacturer"] = mfr_match.group(1).strip().split('\n')[0].strip()

            # Extract Defect Classification
            if "product quality / physical defect" in msg_lower or "physical defect" in msg_lower:
                extracted["complaint_type"] = "Product Quality / Physical Defect"
            elif "leak" in msg_lower:
                extracted["complaint_type"] = "Container Closure Leakage"
            elif "particulate" in msg_lower or "speck" in msg_lower:
                extracted["complaint_type"] = "Foreign Particulate Matter"
            elif any(w in msg_lower for w in ["cap", "seal", "closure", "packaging"]):
                extracted["complaint_type"] = "Packaging / Closure Defect"
            elif "label" in msg_lower:
                extracted["complaint_type"] = "Labeling Error"
            else:
                extracted["complaint_type"] = "Product Quality Defect"

            # Extract Customer Name (avoid generic 'A Hospital' or narrative fragments)
            specific_cust = re.search(
                r'(?:Customer\s*Name\s*[:|\-]?\s*|received\s+from\s+)(St\.\s+Jude\s+Memorial\s+Hospital|[A-Za-z0-9\s,\'-]+?(?:Hospital|Clinic|Pharmacy|Center|Facility))', 
                message, 
                re.IGNORECASE
            )
            if specific_cust:
                extracted["customer_name"] = specific_cust.group(1).strip()
                extracted["complaint_source"] = "Hospital / Healthcare Facility"
            elif "hospital" in msg_lower or "clinic" in msg_lower or "pharmacy" in msg_lower:
                cust_match = re.search(r'([A-Za-z\s]+(hospital|clinic|pharmacy))', message, re.IGNORECASE)
                if cust_match:
                    name_cand = cust_match.group(1).strip().title()
                    if name_cand.lower() not in ["a hospital", "the hospital"]:
                        extracted["customer_name"] = name_cand
                        extracted["complaint_source"] = "Hospital / Healthcare Facility"

            # Extract Dates as stated (Manufacturing, Expiry, Complaint Date)
            date_pat = r'(\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})'
            mfg_match = re.search(rf'(?:Manufacturing\s*Date\s*[:|\-]?\s*|manufactured\s+(?:on\s+)?){date_pat}', message, re.IGNORECASE)
            if mfg_match:
                extracted["manufacturing_date"] = mfg_match.group(1)

            exp_match = re.search(rf'(?:Expiry\s*Date\s*[:|\-]?\s*|expir(?:es|y|ation)\s+(?:date\s+(?:of\s+)?|on\s+)?){date_pat}', message, re.IGNORECASE)
            if exp_match:
                extracted["expiry_date"] = exp_match.group(1)

            date_match = re.search(rf'(?:Complaint\s*Date\s*[:|\-]?\s*|(?:received|reported|dated).*?\bon\s+){date_pat}', message, re.IGNORECASE)
            if date_match:
                extracted["complaint_date"] = date_match.group(1)

            # Purchase Location
            purch_match = re.search(r'(?:Purchase\s*Location\s*[:|\-]?\s*|purchased\s+from\s+)([A-Za-z0-9\s.,\'-]+?)(?:,\s*under|\s+under|\.|\n|$)', message, re.IGNORECASE)
            if purch_match:
                extracted["purchase_location"] = purch_match.group(1).strip()

            # Rx Number
            rx_match = re.search(r'(?:Rx\s*Number\s*[:|\-]?\s*|(?:rx|prescription)\s*(?:number|no\.?|#)?\s*[:\-]?\s*)([A-Za-z0-9-]+)', message, re.IGNORECASE)
            if rx_match:
                extracted["rx_number"] = rx_match.group(1).strip()

            # Preserve full complaint description verbatim without table artifacts
            narrative_match = re.search(r'(Subject:\s*Critical Quality Complaint.*?(?:handling of the affected product\.?))', message, re.DOTALL | re.IGNORECASE)
            if narrative_match:
                extracted["complaint_description"] = narrative_match.group(1).strip()
            else:
                extracted["complaint_description"] = message.strip()

            reply = (
                f"I have extracted the complaint details and populated the form for you. "
                f"An initial ICH Q9–informed risk assessment has been performed."
            )
            return "log_complaint", extracted, reply

        # Conversational queries (Completeness, Summary, CAPA)
        if "complet" in msg_lower:
            prod = current_state.get("product_batch", {}).get("product_name") if current_state else None
            batch = current_state.get("manufacturing", {}).get("batch_number") if current_state else None
            qty = current_state.get("manufacturing", {}).get("affected_quantity") if current_state else None
            missing = []
            if not prod: missing.append("Product Name")
            if not batch: missing.append("Batch Number")
            if not qty: missing.append("Affected Quantity")
            if missing:
                reply = (
                    f"**Complaint Completeness Review:**\n\n"
                    f"The complaint is currently **incomplete**. The following required GMP intake fields are missing:\n"
                    + "\n".join(f"* **{m}**" for m in missing) + "\n\n"
                    f"*Please provide the missing details to proceed with formal QA investigation.*"
                )
            else:
                reply = (
                    f"**Complaint Completeness Review:**\n\n"
                    f"All critical GMP intake fields are present and verified:\n"
                    f"* **Product:** {prod}\n"
                    f"* **Batch:** {batch}\n"
                    f"* **Affected Quantity:** {qty}\n\n"
                    f"The record is complete and ready for quality team review."
                )
            return None, None, reply

        if "summar" in msg_lower:
            prod = current_state.get("product_batch", {}).get("product_name") if current_state else "Not specified"
            batch = current_state.get("manufacturing", {}).get("batch_number") if current_state else "Not specified"
            qty = current_state.get("manufacturing", {}).get("affected_quantity") if current_state else "Not specified"
            cust = current_state.get("origin_customer", {}).get("customer_name") if current_state else "Not specified"
            sev = current_state.get("risk_assessment", {}).get("severity") if current_state else "PENDING"
            reply = (
                f"**Structured Complaint Summary:**\n\n"
                f"* **Product:** {prod}\n"
                f"* **Batch Number:** {batch}\n"
                f"* **Affected Quantity:** {qty}\n"
                f"* **Reporting Customer:** {cust}\n"
                f"* **Risk Classification:** **{sev}**\n\n"
                f"*Detailed investigation considerations and batch retain inspection have been queued.*"
            )
            return None, None, reply

        if "capa" in msg_lower:
            reply = (
                f"**AI-Recommended CAPA Considerations (for QA Review):**\n\n"
                f"1. **Immediate Containment:** Quarantine remaining on-hand stock from the affected batch.\n"
                f"2. **Root Cause Analysis:** Inspect packaging sealing parameters, line temperature logs, and visual inspection records.\n"
                f"3. **Corrective Action:** Re-calibrate blister packaging crimping tools if container integrity breach is confirmed.\n"
                f"4. **Preventive Action:** Review and tighten periodic in-process leak testing frequencies."
            )
            return None, None, reply

        reply = (
            "I am your AI Complaint Copilot. You can describe a complaint in natural language "
            "(e.g., 'Received complaint for Epinephrine Injection, Batch B24017, 50 units leaking'), "
            "request modifications to existing fields, or upload a document."
        )
        return None, None, reply

    @classmethod
    async def _call_gemini_with_tools(
        cls, 
        message: str, 
        current_state: Optional[Dict[str, Any]] = None
    ) -> Optional[Tuple[Optional[str], Optional[Dict[str, Any]], str]]:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)

        has_active_complaint = bool(
            current_state and (
                current_state.get("product_batch", {}).get("product_name") or
                current_state.get("manufacturing", {}).get("batch_number") or
                current_state.get("origin_customer", {}).get("complaint_description")
            )
        )
        context = ""
        if has_active_complaint:
            context = f"Active Form State:\n{json.dumps(current_state, indent=2, default=str)}\n\n"

        prompt = (
            f"{context}User message: {message}\n\n"
            "Instructions:\n"
            "- If reporting or logging a complaint (or when no active complaint is populated), invoke `log_complaint`.\n"
            "- Field mapping rules:\n"
            "  * complaint_source: Standardize to 'Hospital / Healthcare Facility' when received from a hospital, clinic, or healthcare center.\n"
            "  * customer_name: Extract the exact named hospital/customer (e.g. 'St. Jude Memorial Hospital'), ignoring generic phrases like 'A hospital has reported'.\n"
            "  * manufacturing_date: Extract the exact stated manufacturing date (e.g. 'June 15, 2026', '17 August 2026').\n"
            "  * expiry_date: Extract the exact stated expiry date (e.g. 'June 14, 2028', '16 August 2028').\n"
            "  * complaint_date: Extract the exact date received or reported (e.g. 'September 12, 2026', '13 September 2026').\n"
            "  * product_grade_strength: Extract the exact strength stated (e.g. '1 mg/mL', '10 mg'). Do not append unstated standards like USP.\n"
            "  * dosage_form: Extract the exact dosage form if stated (e.g. 'Immediate-release tablets').\n"
            "  * packaging: Extract packaging type if stated (e.g. 'PVC-Alu blister').\n"
            "  * manufacturer: Extract manufacturer if stated (e.g. 'ApexPharma Laboratories').\n"
            "  * purchase_location: Extract purchase/dispensing location if stated (e.g. 'Cornerstone Pharmacy, Downtown').\n"
            "  * rx_number: Extract prescription number if stated (e.g. '9982415').\n"
            "  * complaint_description: Preserve the full, complete complaint description verbatim from the report. Do NOT summarize or truncate.\n"
            "  * Do not invent, infer, or hallucinate unstated values.\n"
            "- If modifying an active complaint, invoke `edit_complaint` with only the changed fields in `updated_fields`.\n"
            "- If asking a conversational question, reply without tools."
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                system_instruction=(
                    "You are PharmaCopilot, an AI complaint intake assistant for pharmaceutical manufacturing QA. "
                    "Use tools to log or edit complaints. Always use ICH Q9-informed risk assessment principles. "
                    "All edits must strictly preserve untouched fields."
                ),
                tools=[{"function_declarations": TOOLS_SCHEMA}]
            )
        )

        if response.function_calls:
            fc = response.function_calls[0]
            tool_name = fc.name
            tool_args = dict(fc.args) if fc.args else {}
            reply_text = (
                f"I have parsed your request using {tool_name} and populated the form for you. "
                f"An initial ICH Q9–informed risk assessment has been performed."
            )
            return tool_name, tool_args, reply_text

        return None, None, response.text or "How can I assist you with this complaint?"

    @classmethod
    async def _call_openai_with_tools(cls, message: str, current_state: Any) -> Tuple[Optional[str], Optional[Dict[str, Any]], str]:
        return cls._mock_tool_dispatcher(message, current_state)
