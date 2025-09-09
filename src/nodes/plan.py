from typing import Dict, Any, Optional
from pydantic import BaseModel, constr
from src.prompts.plan_sql import plan_sql_prompt
from langchain_core.output_parsers import PydanticOutputParser
from src.guardrails.sql_guard import clean_sql_query
from src.llm.factory import chat_model
from src.retriever.retrieve import get_relevant_schema_hint

from src.utils.logging import get_logger

log = get_logger("plan")

# def run_plan_sql(state: Dict[str, Any]) -> Dict[str, Any]:
#     nl_query = state.get("nl_query_effective") or state["nl_query"]
#     schema_hint = get_relevant_schema_hint(nl_query)
#     llm = chat_model(temperature=0.0)
#     sql = llm.invoke(plan_prompt.build(nl_query, schema_hint)).content.strip()
#     state["schema_hint"] = schema_hint
#     state["proposed_sql"] = sql
#     return state


class SQLResponse(BaseModel):
    sql: constr(strip_whitespace=True, min_length=1)  # type: ignore # must be non-empty


parser = PydanticOutputParser(pydantic_object=SQLResponse)


def run_plan_sql(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        nl_query = state.get("nl_query_effective") or state.get("nl_query")
        if not nl_query:
            log.error("No natural language query found in state.")
            state["error"] = "Missing natural language query."
            return state

        schema_hint = get_relevant_schema_hint(nl_query)
        if not schema_hint:
            log.warning("No relevant schema hint found for query: %s", nl_query)

        llm = chat_model(temperature=0.0)

        prompt = plan_sql_prompt | llm  # type: ignore
        prompt = prompt.invoke({"nl_query": nl_query, "schema_hint": schema_hint})
        if not prompt:
            log.error("LLM did not return SQL for query: %s", nl_query)
            state["error"] = "LLM failed to generate SQL."
            return state

        state["schema_hint"] = schema_hint
        state["proposed_sql"] = clean_sql_query(prompt.content.strip())  # type: ignore
        # print(state["proposed_sql"])
        log.info("SQL generated successfully for query: %s", state["proposed_sql"])
        return state

    except Exception as e:
        log.exception("Exception in run_plan_sql: %s", str(e))
        state["error"] = f"Exception: {str(e)}"
        return state
