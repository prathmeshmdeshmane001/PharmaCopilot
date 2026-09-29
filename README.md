# PharmaCopilot: AI-Powered Customer Complaint Intake Prototype

An AI-powered customer complaint intake and triage assistant prototype tailored for pharmaceutical manufacturing quality assurance (Active Pharmaceutical Ingredients & Finished Dosage Forms). 

Built to replicate the enterprise design and UX specified in [`docs/ProblemStatement.md`](docs/ProblemStatement.md) and [`assets/reference-image.png`](assets/reference-image.png).

---

## Key Architecture & Core Constraints

### 1. Two-Column Split-Screen (60 / 40)
- **Left Column (~60%) — Read-Only Customer Complaint Form**:
  - Organised into 4 standard enterprise QA sections:
    1. **Origin & Customer Details** (Source, Customer Name, Complaint Type, Date, Incident Description)
    2. **Product & Batch Identification** (Product Name, Grade/Strength, Batch/Lot Number, Mfg Date, Expiry Date, Affected Quantity & Units)
    3. **Complaint Details** (Classification, Date, Defect Description)
    4. **Risk Assessment** (Severity badge, Priority Level, RPN Score, Rationale, Recommended Actions, Routing, Regulatory Escalation)
  - **Zero-Manual-Edit Architectural Model**: Form inputs render with standard enterprise styling (labels, borders, placeholder values), but are strictly read-only and non-focusable (`readOnly={true}`, `disabled={true}`, `tabIndex={-1}`). Users cannot manually type or alter values directly, and there are **no manual Save or Submit buttons**.
  - **Visual Highlight Pulse Engine**: Any field altered by the AI flashes with an animated indigo ring and an `"AI Updated"` / `"AI Populated"` pill badge for 2.5 seconds.
  - **Audit Trail Drawer**: Clickable header badge exposes complete 21 CFR Part 11–inspired revision history with timestamped field deltas and prompt provenance.

- **Right Column (~40%) — AI Complaint Copilot**:
  - **Document Dropzone**: Drag-and-drop ingestion of `.pdf`, `.docx`, `.txt`, and `.eml` files (up to 10MB).
  - **Text / Email Paste Modal**: Dialog for instant ingestion of raw customer emails or incident narratives.
  - **Extraction Progress Bar**: Real-time progress percentage during document parsing and entity extraction.
  - **Conversational Chat Stream**: Message history with tool execution badges (`[✓ Log Complaint]`, `[✓ Updated affected_quantity: 50 → 75]`, `[✓ Risk Assessment: CRITICAL]`).
  - **Suggested Action Chips**: One-click quick actions for rapid triage evaluation.
  - **Sticky Chat Input Bar**: Conversational input with loading indicators and regulatory notice.

---

## Regulatory Phrasing & Prototype Scope

In accordance with compliance guidelines:
- **Risk Assessment**: Uses an **“ICH Q9–informed risk assessment”** model (utilising Severity, Probability, and Detectability matrices with automatic Critical guardrails for sterile breaches).
- **Auditability**: **“Designed with auditability principles inspired by 21 CFR Part 11”** (immutable audit records, previous/new value logging, timestamping, user prompt provenance).
- **Prototype Scope**: This software is an engineering **prototype** demonstrating automated intake and triage patterns.

---

## The 3 Mandatory Workflows

### Workflow 1: Natural Language Complaint Intake (`log_complaint`)
Users describe a complaint in conversational natural language. The AI parses the text into structured pharmaceutical entities, populates the read-only form with visual highlight pulses, and executes an ICH Q9–informed risk assessment.
> **Sample Prompt:**  
> *"Customer reported 50 vials of Epinephrine 1mg/mL Batch B24017 leaking around rubber seal at Mercy General Hospital on 2026-03-10."*
> 
> **Result:** Automatically sets severity to `CRITICAL`, priority to `P1 - Immediate Action Required`, flags mandatory regulatory escalation (sterile injectable seal failure), routes to Quality Assurance and Pharmacovigilance, and logs the initial audit entry.

### Workflow 2: Conversational Modification with Strict Preservation (`edit_complaint`)
Users can request modifications conversationally. The agent identifies the field delta, updates **only** the requested field, strictly preserves all other existing data, recalculates risk if the changed field is a risk factor, and highlights the updated field.
> **Sample Prompt:**  
> *"Actually, the affected quantity was 75 units, not 50."*
> 
> **Result:** Updates only `affected_quantity` from 50 to 75. All product names, batch numbers, dates, and customer details remain strictly preserved. The audit trail logs an update delta.

### Workflow 3: Document Upload & Seamless Follow-Up (`extract_from_document`)
Users can drag & drop or upload real-world files (PDF, DOCX, TXT, EML) up to 10MB or paste raw text. The ingestion pipeline extracts complaint details, populates the form, and allows immediate natural language follow-up edits.
> **Sample Follow-Up Prompt:**  
> *"The batch number is actually B24099."*
> 
> **Result:** Modifies the batch number while maintaining all extracted document entities.

---

## Repository Structure

```
PharmaCopilot/
├── run.bat                            # Windows one-click batch launcher
├── run.ps1                            # Windows PowerShell launcher
├── docs/                              # Comprehensive architecture & engineering specs
│   ├── ProblemStatement.md           # Original specification
│   ├── architecture.md               # System architecture & 7 Mermaid diagrams
│   ├── implementation.md             # 8-phase implementation roadmap
│   ├── decision.md                   # ADRs (ADR-01 through ADR-07)
│   ├── edge-cases.md                 # Edge-cases & guardrails matrix
│   ├── tests.md                      # QA test plan
│   └── eval.md                       # Benchmarks (TC-01 through TC-10)
├── sample_data/                       # Test documents for Workflow 3
│   ├── sample_complaint.txt          # Plain text incident narrative
│   ├── sample_complaint_letter.pdf   # Formatted clinical complaint letter (PDF)
│   ├── sample_email_complaint.eml    # RFC 822 hospital email complaint (EML)
│   └── sample_packaging_defect.docx  # Quality assurance investigation report (DOCX)
├── backend/                           # FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI application entrypoint
│   │   ├── config.py                 # Application settings & API keys
│   │   ├── models/complaint.py       # Pydantic schemas (ComplaintRecord, RiskAssessment, AuditEntry)
│   │   ├── services/
│   │   │   ├── agent.py              # Central agent coordinator
│   │   │   ├── llm.py                # Dual-mode (Gemini/OpenAI + deterministic heuristic fallback)
│   │   │   ├── tools.py              # Tool handlers (log_complaint, edit_complaint, extract_from_document)
│   │   │   ├── risk_engine.py        # ICH Q9–informed risk calculation & sterile guardrails
│   │   │   └── document_parser.py    # Multi-format parser (PDF, DOCX, TXT, EML)
│   │   ├── store/state_store.py      # In-memory thread-safe state store & audit trail
│   │   └── routers/
│   │       ├── chat.py               # /api/chat, /api/complaints/active, /api/complaints/reset
│   │       ├── documents.py          # /api/documents/upload, /api/documents/paste
│   │       └── health.py             # /api/health
│   ├── requirements.txt              # Python dependencies
│   └── test_prototype.py             # Automated end-to-end verification script
└── frontend/                          # Vite React 19 + TypeScript + Tailwind CSS
    ├── src/
    │   ├── App.tsx                   # 60/40 Split layout container
    │   ├── types/complaint.ts        # TypeScript domain models
    │   ├── store/
    │   │   ├── useComplaintStore.ts  # Form state & visual highlight timers
    │   │   └── useChatStore.ts       # Chat stream, document upload & paste actions
    │   └── components/
    │       ├── form/                 # Left column (60%)
    │       │   ├── ComplaintFormContainer.tsx
    │       │   ├── OriginCustomerSection.tsx
    │       │   ├── ProductBatchSection.tsx
    │       │   ├── ComplaintDetailsSection.tsx
    │       │   ├── RiskAssessmentSection.tsx
    │       │   └── controls/ReadOnlyField.tsx
    │       └── copilot/              # Right column (40%)
    │           ├── CopilotContainer.tsx
    │           ├── CopilotHeader.tsx
    │           ├── DocumentDropzone.tsx
    │           ├── ExtractionProgressBar.tsx
    │           ├── ChatMessageItem.tsx
    │           ├── SuggestedPrompts.tsx
    │           ├── ChatInputBar.tsx
    │           └── PasteModal.tsx
    └── package.json
```

---

## Quick Start Guide

### Prerequisites
- **Python 3.10+** (Python 3.14 compatible)
- **Node.js 18+** and **npm**

### Option A: One-Click Startup (Windows)
Double-click `run.bat` (or run `./run.ps1` in PowerShell).  
This automatically starts both the FastAPI backend and Vite frontend development server in separate windows.

### Option B: Manual Startup

1. **Start the Backend:**
   ```bash
   cd backend
   # If .venv does not exist: python -m venv .venv && .\.venv\Scripts\activate && pip install -r requirements.txt
   .\.venv\Scripts\activate
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *The backend API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).*

2. **Start the Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *Open [http://localhost:5173](http://localhost:5173) in your browser.*

---

## Automated Verification & Testing

PharmaCopilot includes an end-to-end test suite testing all 3 workflows, state delta preservation, sterile override guardrails, zero-manual-edit rules, and regulatory wording adherence:

```bash
cd backend
.\.venv\Scripts\python.exe test_prototype.py
```

To run the complete pytest test suite (25 unit and integration tests):
```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

To test the frontend production build:
```bash
cd frontend
npm run build
```

---

## License & Compliance Notice

This project is developed as an engineering prototype for pharmaceutical complaint triage demonstration purposes.  
- Risk evaluations are **ICH Q9–informed risk assessments**.
- Audit trails are **designed with auditability principles inspired by 21 CFR Part 11**.
