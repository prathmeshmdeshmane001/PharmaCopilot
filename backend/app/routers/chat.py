from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.models.complaint import ComplaintRecord
from app.services.agent import AgentService, AgentTurnResult
from app.store.state_store import store

router = APIRouter(prefix="/api", tags=["Chat & Agent"])

class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural-language instruction or complaint description")
    session_id: str = Field(default="default", description="Session identifier for multi-turn state isolation")

class ChatResponse(BaseModel):
    message: str
    complaint: ComplaintRecord
    diffs: Dict[str, Any]
    tool_badges: List[str]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Primary chat intake endpoint. Users interact strictly via natural language.
    The AI invokes log_complaint, edit_complaint, or answers inquiries,
    synchronizing the read-only form state.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    result: AgentTurnResult = await AgentService.handle_user_turn(
        session_id=payload.session_id,
        message=payload.message
    )

    return ChatResponse(
        message=result.message,
        complaint=result.complaint,
        diffs=result.diffs,
        tool_badges=result.tool_badges
    )

class ResetRequest(BaseModel):
    session_id: str = "default"

@router.get("/complaints/active", response_model=ComplaintRecord)
async def get_active_complaint(session_id: str = "default"):
    """Fetches the active complaint record for the given session."""
    return store.get_or_create_complaint(session_id)

@router.post("/complaints/reset", response_model=ComplaintRecord)
async def reset_complaint(payload: Optional[ResetRequest] = None):
    """Resets the complaint form state to empty for the session."""
    session_id = payload.session_id if payload else "default"
    return store.reset_session(session_id)
