from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.models.complaint import ComplaintRecord
from app.services.document_parser import DocumentParser, MAX_FILE_SIZE_BYTES
from app.services.tools import ToolsService
from app.services.agent import AgentService, AgentTurnResult

router = APIRouter(prefix="/api/documents", tags=["Document Ingestion"])

class DocumentPasteRequest(BaseModel):
    text: str = Field(..., description="Pasted raw email or complaint text")
    session_id: str = Field(default="default", description="Session identifier")

class DocumentUploadResponse(BaseModel):
    message: str
    complaint: ComplaintRecord
    diffs: Dict[str, Any]
    tool_badges: List[str]
    filename: str
    format: str
    extracted_fields_count: int

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form("default")
):
    """
    Ingests and extracts structured complaint records from PDF, DOCX, TXT, or EML files.
    Automatically hydrates the read-only complaint form and generates an ICH Q9-informed risk assessment.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400, 
            detail=f"File exceeds maximum allowed size of 10MB (Received {len(content) / (1024*1024):.1f}MB)."
        )

    try:
        raw_text, doc_format = DocumentParser.parse_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    try:
        result: AgentTurnResult = await AgentService.handle_user_turn(
            session_id=session_id,
            message=raw_text
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to extract complaint entities: {str(e)}")

    assistant_msg = (
        f"Successfully extracted {len(result.diffs)} attributes from {doc_format} '{file.filename}'. "
        f"The complaint record has been populated and evaluated under ICH Q9 Quality Risk Management principles. "
        f"You can request any further adjustments using natural language."
    )

    tool_badges = [f"[✓ Document Extraction: {file.filename[:20]}]"] + [b for b in result.tool_badges if "Document Extraction" not in b]

    return DocumentUploadResponse(
        message=assistant_msg,
        complaint=result.complaint,
        diffs=result.diffs,
        tool_badges=tool_badges,
        filename=file.filename,
        format=doc_format,
        extracted_fields_count=len(result.diffs)
    )
 
@router.post("/paste", response_model=DocumentUploadResponse)
async def paste_document_text(payload: DocumentPasteRequest):
    """
    Parses pasted email or complaint narrative into structured complaint fields
    using the unified Agent/LLM extraction pipeline.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Pasted text cannot be empty.")

    result: AgentTurnResult = await AgentService.handle_user_turn(
        session_id=payload.session_id,
        message=payload.text
    )

    return DocumentUploadResponse(
        message=result.message,
        complaint=result.complaint,
        diffs=result.diffs,
        tool_badges=result.tool_badges,
        filename="Pasted_Text.txt",
        format="Pasted Text",
        extracted_fields_count=len(result.diffs)
    )

