from typing import Dict, Any
from src.llm.factory import chat_model
from src.retriever.retrieve import get_relevant_schema_hint
from src.guardrails.sql_guard import clean_sql_query
from src.prompts.plan_sql_with_enrichments import plan_sql_with_enrichments_router
from src.utils.logging import get_logger
log = get_logger("plan_with_enrichments")



def run_plan_with_enrichments(state: Dict[str, Any]) -> Dict[str, Any]:
    nl_query = state.get("nl_query_effective") or state["nl_query"]
    enrichments = state.get("enrichments", {})
    schema_hint = get_relevant_schema_hint(nl_query)

    llm = chat_model(temperature=0.0)
    prompt = plan_sql_with_enrichments_router | llm  # pyright: ignore[reportOperatorIssue]
    prompt = prompt.invoke({"nl_query": nl_query, "schema_hint": schema_hint, "enrichments": enrichments})

    state["schema_hint"] = schema_hint
    state["proposed_sql"] = clean_sql_query(prompt.content.strip()) # type: ignore
    log.info("SQL generated successfully for query: %s", nl_query)
    return state




