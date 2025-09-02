from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from src.graph.graph import build_graph
from src.memory.store import memory
from src.utils.logging import get_logger

log = get_logger("app")
graph = build_graph()
app = FastAPI(title="NL2SQL Snowflake Agent")

class QueryRequest(BaseModel):
    session_id: str = Field(..., description="Conversation session ID")
    query: str = Field(..., description="User natural language question")
    metadata: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    session_id: str
    intent: str
    sql: Optional[str] = None
    columns: Optional[List[str]] = None
    rows: Optional[List[Any]] = None
    error: Optional[str] = None
    clarifying_question: Optional[str] = None
    awaiting_clarification: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    # Append user message to memory
    history_msgs = memory.get(req.session_id)
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history_msgs])
    memory.append(req.session_id, "user", req.query)

    # Build initial state for the graph
    state = {
        "session_id": req.session_id,
        "nl_query": req.query,
        "history_text": history_text
    }

    # Run the LangGraph agent
    try:
        result_state = graph.invoke(state) # type: ignore
    except Exception as e:
        log.error("Graph execution failed", extra={"extra": {"error": str(e)}})
        return QueryResponse(
            session_id=req.session_id,
            intent="error",
            error=str(e)
        )

    # Append system/agent response to memory
    if result_state.get("clarifying_question"):
        memory.append(req.session_id, "assistant", result_state["clarifying_question"])
    elif result_state.get("rows") is not None:
        # Summarize result for memory
        summary = f"Returned {len(result_state['rows'])} rows."
        memory.append(req.session_id, "assistant", summary)

    return QueryResponse(
        session_id=req.session_id,
        intent=result_state.get("intent", ""),
        sql=result_state.get("final_sql"),
        columns=result_state.get("columns"),
        rows=result_state.get("rows"),
        error=result_state.get("error"),
        clarifying_question=result_state.get("clarifying_question"),
        awaiting_clarification=result_state.get("awaiting_clarification", False),
        metadata={"reason": result_state.get("intent_reason")}
    )

@app.get("/health")
def health():
    return {"status": "ok"}
