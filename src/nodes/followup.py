from typing import Dict, Any
from src.llm.factory import chat_model
from src.prompts.rewrite_followup import rewrite_followup
from src.pydantic.prompt_validate import rewritten_parser
from src.utils.logging import get_logger
log = get_logger("followup")

def run_followup_rewrite(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        llm = chat_model(temperature=0.0)
        resp = rewrite_followup | llm | rewritten_parser # type: ignore
        rewritten = resp.invoke({"followup": state["nl_query"], "history": state.get('history_text', '')})
        if rewritten is None:
            log.error("Failed to rewrite query; rewritten is None.")
            state["nl_query_effective"] = state.get("nl_query", "").strip()
            return state
        state["nl_query_effective"] = rewritten.get("nl_query_effective", state["nl_query"]).strip()
        return state
    except Exception as e:
        log.error(f"Exception in run_followup_rewrite: {e}")
        state["nl_query_effective"] = state.get("nl_query", "").strip()
        return state
