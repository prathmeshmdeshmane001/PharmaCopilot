# PharmaCopilot — AI Evaluation & Benchmark Framework

This document defines the evaluation framework, quality benchmarks, and accuracy metrics for assessing the PharmaCopilot prototype across extraction accuracy, state preservation, and risk assessment reliability.

---

## 1. Evaluation Objectives

The evaluation framework verifies five core dimensions of the AI copilot:
1. **Entity Extraction Precision & Recall**: Accuracy in converting natural language narratives and documents into structured fields.
2. **State Preservation Fidelity**: Zero unintended mutations during `edit_complaint` operations.
3. **Risk Assessment Clinical Alignment**: Consistency of the **ICH Q9–informed risk assessment** against pharmaceutical quality standards.
4. **Zero-Manual-Edit Integrity**: Absolute enforcement of AI-only form mutations.
5. **Latency & Usability**: Responsive interaction suitable for quality operations.

---

## 2. Evaluation Metrics & Target Benchmarks

| Dimension | Metric | Formula / Definition | Prototype Target |
| :--- | :--- | :--- | :---: |
| **Field Extraction Accuracy** | Field-level F1 Score | Harmonic mean of precision and recall across extracted entities (Product, Batch, Dates, Qty). | $\ge 92\%$ |
| **Batch Identification Accuracy** | Exact Match Rate | Exact string match for lot/batch codes (e.g. `B24017`). | $\ge 95\%$ |
| **State Preservation Rate** | Unintended Mutation Rate | $\frac{\text{Unintended Modified Fields}}{\text{Total Untouched Fields}}$ during `edit_complaint`. | **$0.0\%$ (Strict Zero)** |
| **Risk Classification Accuracy** | Severity Agreement | Exact match with expert clinical benchmark (`CRITICAL`, `HIGH`, `MED`, `LOW`). | $\ge 90\%$ |
| **Safety Override Recall** | Sterile Breach Recall | Proportion of sterile/injectable compromises correctly clamped to `CRITICAL`. | **$100\%$ (Mandatory)** |
| **Document Parsing Fidelity** | Key Data Recall | Extraction rate of essential complaint attributes from multi-format files (PDF, DOCX, EML). | $\ge 88\%$ |
| **Inference Latency** | End-to-End Chat Latency | Time from user query to completed response with populated state. | $< 3.0\text{s}$ (Live LLM) |

---

## 3. Benchmark Dataset (Golden Test Scenarios)

The evaluation suite tests 10 diverse pharmaceutical test scenarios:

| Case ID | Scenario Category | Input Description | Expected Extracted Entities | Expected Risk Level |
| :---: | :--- | :--- | :--- | :---: |
| **TC-01** | Sterile Injectable Leak | Epinephrine 1mg/mL, Batch B24017, 50 ampoules leaking around seal. | Product: Epinephrine Inj<br/>Batch: B24017<br/>Qty: 50 ampoules | **CRITICAL**<br/>(Sterility Override) |
| **TC-02** | Solid Oral Dose Defect | Metformin 500mg, Batch M901, 20 bottles missing child safety caps. | Product: Metformin 500mg<br/>Batch: M901<br/>Qty: 20 bottles | **MEDIUM**<br/>(Closure defect, non-sterile) |
| **TC-03** | Particulate in Infusion | Normal Saline 0.9% 500mL, Lot NS44, floating black specks in 2 bags. | Product: Normal Saline<br/>Batch: NS44<br/>Qty: 2 bags | **CRITICAL**<br/>(Foreign particulate) |
| **TC-04** | Secondary Packaging Scuff | Ibuprofen 200mg, Lot IB12, crumpled outer carton reported by retail store. | Product: Ibuprofen 200mg<br/>Batch: IB12<br/>Qty: 1 carton | **LOW**<br/>(Cosmetic secondary) |
| **TC-05** | Ambiguous Multi-Date | Manufactured Oct 2025, received Feb 2026, expiring Oct 2027. | Correctly differentiates mfg_date (`2025-10-01`) vs expiry_date (`2027-10-01`). | N/A |
| **TC-06** | Complex Document (PDF) | Scanned hospital QA incident report with tabular product data. | Complete extraction of hospital name, product, batch, dates, and narrative. | **HIGH** |
| **TC-07** | Email Ingestion (.EML) | Customer service email chain regarding broken blister seals. | Extraction of sender email, product name, and affected blister count. | **MEDIUM** |
| **TC-08** | Delta Edit (Quantity) | *"Actually, the affected quantity is 75 units, not 50."* | Updates `affected_quantity: 75`, strictly preserves Product and Batch. | Re-evaluated |
| **TC-09** | Delta Edit (Batch) | *"The lot number is B24099, please correct it."* | Updates `batch_number: B24099`, preserves all other fields. | Preserved |
| **TC-10** | Missing Information | Vague complaint: *"Our clinic received damaged vials."* | Extracts description, sets batch and quantity to `null`/unspecified. | Flags Missing Info |

---

## 4. Evaluation Execution Procedure

```bash
# Run automated benchmark evaluation script
cd backend
python -m tests.run_eval --dataset=benchmark_cases.json --mode=mock

# Run live LLM evaluation (requires API key)
python -m tests.run_eval --dataset=benchmark_cases.json --mode=live
```

### Evaluation Output Format
```json
{
  "total_cases": 10,
  "passed_cases": 10,
  "field_f1_score": 0.94,
  "state_preservation_score": 1.0,
  "safety_override_recall": 1.0,
  "average_latency_seconds": 1.82,
  "status": "PASS"
}
```

---

## 5. Human-in-the-Loop Review Criteria

For QA teams evaluating the prototype:
1. **Zero Manual Edits**: Confirm that neither typing nor clicking inside form fields alters complaint values.
2. **Visual Feedback**: Verify that field updates trigger the 2.5-second highlight pulse and display the `"AI Updated"` badge.
3. **Audit Trail Inspection**: Verify that each interaction generates an immutable audit record with user prompt and field delta.
4. **Chat Transparency**: Verify that every AI response explicitly identifies tool actions taken via badges (`[✓ Log Complaint]`, `[✓ edit_complaint]`).
