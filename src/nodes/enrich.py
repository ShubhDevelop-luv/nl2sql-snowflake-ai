# src/nodes/enrich.py
import json
from typing import Dict, Any
from src.llm.factory import chat_model
from src.utils.enrichment import apply_edit_semantics
from src.prompts.enrichment import enrichment_prompt
from src.utils.logging import get_logger    
log = get_logger("enrich")

def run_extract_enrichments(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract deterministic facts, keywords, geography, industry codes, and action type
    from the NL query, then merge into persistent enrichment state.
    """
    llm = chat_model(temperature=0.0)
    prompt = enrichment_prompt | llm  # type: ignore
    resp = prompt.invoke({"nl_query": state["nl_query"]})
    try:
        data = json.loads(resp) # pyright: ignore[reportArgumentType]
    except Exception:
        data = {}

    # Merge with existing enrichments using edit semantics
    current = state.get("enrichments", {})
    updated = apply_edit_semantics(current, data)
    state["enrichments"] = updated
    state["enrichment_active"] = bool(updated)

    # Store deterministic + keywords for downstream planning
    state["deterministic"] = data.get("deterministic", {})
    state["keywords"] = data.get("keywords", [])

    # Keep the raw extraction for debugging/observability
    state["last_enrichment_extraction"] = data

    return state
