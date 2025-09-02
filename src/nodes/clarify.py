from typing import Dict, Any
from src.llm.factory import chat_model
from src.prompts.clarify import clarify_prompt
from src.pydantic.prompt_validate import clarify_parser
from src.utils.logging import get_logger
log = get_logger("clarify")


def run_clarify(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        log.info("Starting clarification process.")
        llm = chat_model(temperature=0.3)
        log.debug(f"Invoking LLM with history_text: {state.get('history_text', '')} and nl_query: {state['nl_query']}")
        q = clarify_prompt | llm | clarify_parser # type: ignore
        q = q.invoke({"nl_query": state["nl_query"], "history": state.get('history_text', '')}) # type: ignore
        state["clarifying_question"] = q.get("clarifying_question", "").strip().rstrip("?") + "?"
        state["awaiting_clarification"] = True
        log.info(f"Clarifying question generated: {state['clarifying_question']}")
        return state
    except Exception as e:
        log.error(f"Error in run_clarify: {e}", exc_info=True)
        state["clarifying_question"] = None
        state["awaiting_clarification"] = False
        state["error"] = str(e)
        return state
