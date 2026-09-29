# PharmaCopilot — Architectural Decision Records (ADR)

This document captures key design, architectural, and technology decisions for the PharmaCopilot prototype, grounded in [`docs/ProblemStatement.md`](file:///c:/PharmaCopilot/docs/ProblemStatement.md), [`docs/architecture.md`](file:///c:/PharmaCopilot/docs/architecture.md), and [`docs/implementation.md`](file:///c:/PharmaCopilot/docs/implementation.md).

---

## ADR-01: Split-Screen Layout (60% Form / 40% Copilot)

* **Status:** Accepted
* **Context:** The problem statement requires natural language complaint logging, document ingestion, risk assessment, and live visual representation without manual form editing. The provided reference interface ([`assets/reference-image.png`](file:///c:/PharmaCopilot/assets/reference-image.png)) demonstrates a side-by-side workspace.
* **Decision:** Implement a 60/40 two-column split-screen layout:
  - **Left (60%):** Structured Customer Complaint Form organized into 4 clinical sections.
  - **Right (40%):** AI Complaint Copilot with drag-and-drop document upload, extraction progress indicator, chat history with tool badges, suggested prompts, and input bar.
* **Consequences:** Provides immediate visual feedback when the AI updates complaint fields while maintaining a chat-first interaction model.

---

## ADR-02: Zero-Manual-Edit Enforcement Mechanism

* **Status:** Accepted
* **Context:** The problem statement strictly mandates that users **must not manually fill or edit the complaint form**.
* **Decision:** Enforce read-only interaction across two layers:
  1. **UI Layer:** Form fields are rendered using custom read-only input components (`readOnly={true}`, `tabIndex={-1}`, `cursor-default`). No manual Save or Edit buttons exist on the form. A prominent `🔒 AI Managed Form` badge is displayed.
  2. **API Layer:** The backend exposes no direct field mutation endpoints (`PUT /api/complaints/field`). The only mutation vector is the agent tool pipeline (`POST /api/chat` and `POST /api/documents/upload`).
* **Consequences:** Guarantees that all updates originate from natural language or uploaded documents and are processed through the AI tools and audit log.

---

## ADR-03: Partial State Merging via JSON Merge Patch for `edit_complaint`

* **Status:** Accepted
* **Context:** When users edit an existing complaint (e.g., *"Change the affected quantity to 75 units"*), the AI must update only the requested fields while strictly preserving all other existing fields.
* **Decision:** The `edit_complaint` tool returns an `updated_fields` delta dictionary. The backend applies an atomic patch:
  $$\text{State}_{t+1} = \text{State}_t \oplus \Delta_{\text{tool}}$$
  Fields not included in $\Delta_{\text{tool}}$ are strictly preserved.
* **Consequences:** Eliminates accidental data overwrites and ensures predictable state synchronization between conversation and form.

---

## ADR-04: Hybrid Risk Assessment (ICH Q9–Informed + Guardrails)

* **Status:** Accepted
* **Context:** Risk evaluation must determine severity, priority, reasoning, routing, and actions. Regulated pharmaceutical contexts require predictable safety boundaries.
* **Decision:** Use an **ICH Q9–informed risk assessment** combining:
  1. A quantitative Risk Priority Number matrix ($\text{RPN} = \text{Severity} \times \text{Probability} \times \text{Detectability}$).
  2. Hardcoded safety overrides (e.g., any sterile injectable defect like leaks or particulates is clamped to `CRITICAL` / `P1`).
  3. LLM-generated clinical reasoning and departmental routing (e.g., Quality Assurance, Sterile Ops).
* **Consequences:** Guarantees safety-critical consistency while providing contextual, natural-language rationales.

---

## ADR-05: Multi-Format Document Ingestion Engine

* **Status:** Accepted
* **Context:** Customers and quality teams submit complaints in diverse formats (PDFs, Word documents, text files, and emails).
* **Decision:** Support four primary formats up to 10MB using dedicated lightweight libraries:
  - **PDF:** `pdfplumber` for tabular and structured text; `pypdf` fallback.
  - **DOCX:** `python-docx` for paragraphs and tables.
  - **EML:** Python standard `email` library for headers (`From`, `Subject`, `Date`) and message body.
  - **TXT:** Native text parser with whitespace sanitization.
* **Consequences:** Covers all common complaint channels without external heavy OCR services in the prototype.

---

## ADR-06: Dual AI Execution Mode (Live LLM + Offline Mock Fallback)

* **Status:** Accepted
* **Context:** The prototype must demonstrate real LLM reasoning (via Gemini / OpenAI) while ensuring robust evaluation even when offline, rate-limited, or running in air-gapped test environments.
* **Decision:** Build the `AgentService` with two execution providers:
  - **Live Provider:** Native Gemini 2.0 / OpenAI Function Calling.
  - **Mock Provider:** Deterministic regex/heuristic engine that extracts entities and simulates tool execution badges when API keys are absent.
* **Consequences:** Guarantees zero downtime during prototype demonstration and evaluation.

---

## ADR-07: In-Memory Session Store with Auditability Principles Inspired by 21 CFR Part 11

* **Status:** Accepted
* **Context:** The prototype requires change tracking and version history without the overhead of external database servers or complex migrations.
* **Decision:** Implement a lightweight, dictionary-backed session store in FastAPI that logs every mutation into an immutable `AuditEntry` list (recording timestamp, user prompt, actor, and field deltas).
* **Consequences:** Meets the requirement: **designed with auditability principles inspired by 21 CFR Part 11**, while keeping the prototype setup fast, zero-dependency, and easily reproducible.
