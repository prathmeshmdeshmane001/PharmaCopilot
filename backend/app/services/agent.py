from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.models.complaint import ComplaintRecord
from app.store.state_store import store
from app.services.llm import LLMService
from app.services.tools import ToolsService

class AgentTurnResult(BaseModel):
    message: str
    complaint: ComplaintRecord
    diffs: Dict[str, Any]
    tool_badges: List[str]

class AgentService:
    """
    Central AI orchestrator that coordinates natural language intent,
    tool execution, deterministic state merging, and audit trail logging.
    """

    @classmethod
    async def handle_user_turn(
        cls,
        session_id: str,
        message: str
    ) -> AgentTurnResult:
        # 1. Fetch current session state
        active_record = store.get_or_create_complaint(session_id)
        current_state_dict = active_record.model_dump()

        # 2. Process turn via LLM Service (live or deterministic mock)
        tool_name, tool_args, assistant_reply = await LLMService.process_user_turn(
            user_message=message,
            active_complaint=current_state_dict
        )

        diffs: Dict[str, Any] = {}
        tool_badges: List[str] = []

        # 3. Dispatch tool execution if requested
        if tool_name == "log_complaint" and tool_args:
            active_record, diffs, tool_badges = ToolsService.execute_log_complaint(
                session_id=session_id,
                arguments=tool_args,
                user_prompt=message
            )
        elif tool_name == "edit_complaint" and tool_args:
            active_record, diffs, tool_badges = ToolsService.execute_edit_complaint(
                session_id=session_id,
                arguments=tool_args,
                user_prompt=message
            )
        elif tool_name == "extract_from_document" and tool_args:
            active_record, diffs, tool_badges = ToolsService.execute_extract_from_document(
                session_id=session_id,
                arguments=tool_args,
                user_prompt=message
            )

        return AgentTurnResult(
            message=assistant_reply,
            complaint=active_record,
            diffs=diffs,
            tool_badges=tool_badges
        )
