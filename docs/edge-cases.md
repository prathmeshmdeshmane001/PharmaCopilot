# PharmaCopilot — Edge Cases & Failure Handling Strategy

This document details critical edge cases, ambiguous inputs, and operational failure modes across the three core workflows, defining explicit handling strategies for the prototype.

---

## 1. Natural Language Extraction Edge Cases (`log_complaint`)

| Scenario / Edge Case | Example Prompt | Risk / Failure Mode | Handling Strategy |
| :--- | :--- | :--- | :--- |
| **Ambiguous Quantity & Units** | *"A customer received a carton of 10 boxes and noticed 3 vials were cracked."* | Model may extract 10 boxes, 1 carton, or 3 vials as affected quantity. | System instructions prioritize extracting the **directly affected defective count** (e.g., `affected_quantity: 3`, `unit_of_measure: "vials"`), while recording total pack size in the detailed description. |
| **Multiple Conflicting Dates** | *"Manufactured on 12/01/2025, received on 02/15/2026, expiry 12/2027, defect seen yesterday."* | Confusion between `manufacturing_date`, `expiry_date`, and `complaint_date`. | Explicit schema properties: model maps "manufactured on" $\rightarrow$ `manufacturing_date`, "expiry" $\rightarrow$ `expiry_date`, and "defect seen yesterday" $\rightarrow$ `complaint_date` (normalized to ISO `YYYY-MM-DD`). |
| **Vague or Missing Batch Number** | *"Defective Metformin 500mg reported, but customer discarded the outer carton with the batch number."* | Missing regulatory mandatory identifier. | Field is set to `null` or `"Unspecified"`. Detailed description captures that batch details were discarded. Complaint status flags missing batch for triage. |
| **Multi-Entity / Composite Complaints** | *"Received complaints for both Paracetamol batch P101 and Amoxicillin batch A202."* | Attempting to cram two distinct product complaints into a single record. | Agent creates a complaint record for the primary item mentioned, notes the second item in the description, and advises the user to log a separate record for the second product. |

---

## 2. State Preservation & Delta Update Edge Cases (`edit_complaint`)

| Scenario / Edge Case | Example Prompt | Risk / Failure Mode | Handling Strategy |
| :--- | :--- | :--- | :--- |
| **Single Field Edit Overwriting Whole State** | *"Change the batch number to B24099."* | Naive LLM might return an empty schema for other fields, erasing existing data. | The `edit_complaint` tool schema requires a partial delta dictionary (`updated_fields`). The backend merges $\text{State}_{t+1} = \text{State}_t \oplus \Delta$. Unmentioned fields are never cleared. |
| **Explicit Field Deletion / Clearing** | *"Remove the customer name, they requested anonymity."* | Model might ignore the delete instruction or fail to nullify. | If user explicitly asks to remove/clear a field, the tool accepts an explicit `null` in `updated_fields`, replacing the previous value and updating the audit log. |
| **Risk-Bearing vs. Non-Risk Edits** | *"Update customer name to Mercy Hospital"* vs. *"Quantity is actually 10,000 units, not 10."* | Unnecessary risk recalculation vs. failing to escalate risk when exposure increases. | The Risk Engine checks whether modified fields intersect with risk factors (`affected_quantity`, `complaint_type`, `complaint_description`, `batch_number`). Non-risk edits leave the risk score intact. |
| **Conflicting Follow-up Edit** | *"Change affected quantity to twenty-five... wait, make it 30 units."* | Parser might extract both numbers or average them. | Agent extracts the final declared value (`30 units`) and confirms the decision in the conversational response. |

---

## 3. Document Ingestion Edge Cases (`extract_from_document`)

| Scenario / Edge Case | File / Ingestion Context | Risk / Failure Mode | Handling Strategy |
| :--- | :--- | :--- | :--- |
| **Unsupported File Type or Size** | User drops `.xlsx`, `.zip`, or a file $> 10\text{MB}$. | Server crash or unhandled 500 exception. | Client-side dropzone rejects unsupported types with an immediate warning toast. Backend rejects with `400 Bad Request` and descriptive error message. |
| **Scanned / Image-Only PDF** | PDF has no selectable text layer (pure bitmap scan). | `pdfplumber` returns empty string. | In prototype mode, system detects zero extracted characters and prompts: *"This PDF contains scanned images without digital text. Please paste the complaint narrative or use a digital PDF."* |
| **Long Email Chains (.EML)** | Forwarded email with 5 historical replies, disclaimers, and signatures. | Header confusion; model extracts wrong sender or irrelevant thread context. | EML parser extracts top-level `From`, `Subject`, `Date`, strips boilerplates (e.g. *"Confidentiality Notice"*), and feeds clean content to the extraction tool. |
| **Partially Populated Documents** | Document contains product and batch info but no customer name or dates. | Extraction fails schema validation. | All fields except `complaint_description` are optional in the Pydantic schema, allowing partial document extraction without validation errors. |

---

## 4. Risk Assessment & Safety Guardrail Edge Cases

| Scenario / Edge Case | Incident Condition | Risk / Failure Mode | Handling Strategy |
| :--- | :--- | :--- | :--- |
| **Sterile Injectable Defect (Safety Override)** | Defective vial with leak or glass flake in 1 single ampoule of Epinephrine. | Standard calculation might consider quantity 1 as "LOW" risk. | **ICH Q9–informed safety guardrail rule**: If dosage form is injectable/sterile and defect involves closure breach, particulate, or contamination, severity is clamped to `CRITICAL` / Priority `P1` regardless of quantity. |
| **Borderline Risk Priority Number** | Computed RPN is 59 (threshold for CRITICAL is 60). | Arbitrary boundary fluctuation. | Risk Engine provides explainable margin context in `reasoning`: flags complaint as *"High risk approaching Critical threshold; mandatory QA review advised."* |
| **Adverse Drug Reaction Reported** | Complaint mentions: *"Patient experienced anaphylaxis after injection."* | Classified as simple product quality complaint instead of pharmacovigilance alert. | System detects adverse event keywords, sets `requires_regulatory_escalation = true`, and sets routing to `Pharmacovigilance & Quality Assurance`. |

---

## 5. UI & Zero-Manual-Edit Edge Cases

| Scenario / Edge Case | User Action | Risk / Failure Mode | Handling Strategy |
| :--- | :--- | :--- | :--- |
| **Direct Click or Typing on Form Field** | User attempts to click into a field, double-click, or press keyboard keys. | User expects manual text cursor to appear. | Controls have `readOnly={true}`, `tabIndex={-1}`, and `cursor-default`. A visual tooltip gently reminds: *"🔒 AI Managed: Request changes via the Copilot chat."* |
| **Rapid Consecutive Prompts** | User sends multiple messages before the first response finishes. | Out-of-order state overwrites or race conditions. | Chat input disables and displays a loading spinner during active AI inference (`isAiProcessing = true`), queuing requests deterministically. |
| **Simultaneous Field Highlights** | 6 fields populated at once during document extraction. | Cluttered or visually jarring animation flash. | Highlight engine applies a synchronized, gentle 2.5-second pulse across updated fields rather than staggered conflicting animations. |
