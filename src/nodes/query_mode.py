from typing import Dict, Any
from src.llm.factory import chat_model
from src.prompts.query_mode_router import enrichment_prompt 
from src.pydantic.prompt_validate import query_model


def run_query_mode(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = chat_model(temperature=0.0)
    resp = enrichment_prompt | llm | query_model # type: ignore
    data = resp.invoke({"nl_query": state["nl_query"]})
    try:
        state["query_mode"] = data.get("query_mode", "Plan_SQL")
        state["query_mode_reason"] = data.get("reason", "")
    except Exception:
        state["query_mode"] = "Plan_SQL"
        state["query_mode_reason"] = "fallback"
    return state