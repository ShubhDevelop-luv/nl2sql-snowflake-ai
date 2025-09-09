from typing import Dict, Any
from src.llm.factory import chat_model
from src.prompts.query_mode_router import enrichment_prompt 
from src.pydantic.prompt_validate import query_model
from src.utils.logging import get_logger
log = get_logger("query_mode")


def run_query_mode(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        nl_query = state.get("nl_query_effective") or state.get("nl_query")
        if not nl_query:
            log.error("No natural language query found in state.")
            state["error"] = "Missing natural language query."
            return state
        llm = chat_model(temperature=0.0)
        resp = enrichment_prompt | llm | query_model # type: ignore
        data = resp.invoke({"nl_query": nl_query})
        try:
            state["query_mode"] = data.get("query_mode", "Plan_SQL")
            state["query_mode_reason"] = data.get("reason", "")
        except Exception:
            state["query_mode"] = "Plan_SQL"
            state["query_mode_reason"] = "fallback"
        log.info(f"Query mode determined: {state['query_mode']} with reason: {state['query_mode_reason']}")
        return state
    except Exception as e:
        log.exception("Exception in run_plan_sql: %s", str(e))
        state["error"] = f"Exception: {str(e)}"
        return state