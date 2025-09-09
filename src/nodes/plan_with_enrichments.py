from typing import Dict, Any
from src.llm.factory import chat_model
from src.retriever.retrieve import get_relevant_schema_hint
from src.guardrails.sql_guard import clean_sql_query
from src.prompts.plan_sql_with_enrichments import plan_sql_with_enrichments_router
from src.utils.logging import get_logger
log = get_logger("plan_with_enrichments")



# def run_plan_with_enrichments(state: Dict[str, Any]) -> Dict[str, Any]:
#     nl_query = state.get("nl_query_effective") or state["nl_query"]
#     enrichments = state.get("enrichments", {})
#     schema_hint = get_relevant_schema_hint(nl_query)

#     llm = chat_model(temperature=0.0)
#     prompt = plan_sql_with_enrichments_router | llm  # pyright: ignore[reportOperatorIssue]
#     prompt = prompt.invoke({"nl_query": nl_query, "schema_hint": schema_hint, "enrichments": enrichments})

#     state["schema_hint"] = schema_hint
#     state["proposed_sql"] = clean_sql_query(prompt.content.strip()) # type: ignore
#     log.info("SQL generated successfully for query: %s", nl_query)
#     return state

from typing import Dict, Any
from src.llm.factory import chat_model
import json

def run_enrichment(state: Dict[str, Any]) -> Dict[str, Any]:
    spec = state.get("insights_spec", {})
    if not spec:
        state["enriched_rows"] = []
        return state

    llm = chat_model(temperature=0.0)
    enriched_rows = []

    for row in state["rows"]:
        # Convert row to dict for easier merging
        row_dict = dict(zip(state["columns"], row))

        # Build JSON payload for the LLM
        payload = {
            "company_name": row_dict.get("COMPANY_NAME") or row_dict.get("company_name"),
            "company_city": row_dict.get("LOCATION_CITY") or row_dict.get("company_city"),
            "company_state": row_dict.get("LOCATION_STATE_CODE") or row_dict.get("company_state"),
            "insights_spec": spec
        }

        # Send the JSON payload as the prompt
        prompt = json.dumps(payload, ensure_ascii=False)
        resp = llm.invoke(prompt).content # type: ignore

        # Parse LLM output safely
        try:
            data = json.loads(resp) # type: ignore
            # Ensure both keys exist, even if null
            if spec.get("name"):
                data.setdefault(spec["name"], None)
                data.setdefault(f"source_{spec['name']}", None)
        except Exception:
            data = {
                spec.get("name", "unknown"): None,
                f"source_{spec.get('name', 'unknown')}": None
            }

        # Merge enrichment into the original row dict
        enriched_rows.append({**row_dict, **data})

    state["enriched_rows"] = enriched_rows
    log.info(f"Enriched {len(enriched_rows)} rows with insights.")
    return state



