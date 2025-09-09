from typing import Dict, Any
from src.llm.factory import chat_model
from src.prompts.extract_enrichment_spec import extract_enrichment_spec
from src.pydantic.prompt_validate import enrichment_response
import json
from src.utils.logging import get_logger
log = get_logger("extract_enrichment_spec")


def run_extract_enrichment_spec(state: Dict[str, Any]) -> Dict[str, Any]:
    nl_query = state.get("nl_query_effective") or state.get("nl_query")
    llm = chat_model(temperature=0.0)
    resp = extract_enrichment_spec | llm | enrichment_response # type: ignore
    data = resp.invoke({"nl_query": nl_query})
    try:
        state["insights_spec"] = data.get("insights_spec", {})
    except Exception:
        state["insights_spec"] = {}
    log.info(f"Extracted insights_spec: {state['insights_spec']}")
    return state
