import json
from typing import Dict, Any
from src.llm.factory import chat_model
from src.utils.logging import get_logger
log = get_logger("intent")
from src.prompts.intent_router import intent_router
from src.pydantic.prompt_validate import intent_parser

def run_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    nl_query = state["nl_query"]
    history = state.get("history_text", "")
    llm = chat_model(temperature=0.0)
    log.info(f"Running intent detection for query: {nl_query}")
    try:
        intent_sturcture = intent_router | llm | intent_parser # type: ignore
        print("History", history)
        data = intent_sturcture.invoke({"nl_query": nl_query, "history": history})
        if data is None:
            log.error("LLM response has no 'content' attribute")
            raise AttributeError("LLM response has no 'content' attribute")
        log.info(f"LLM response content: {data}") 
        state["intent"] = data.get("intent", "simple_query")
        confidence = data.get("confidence", 0.6)
        try:
            state["intent_confidence"] = float(confidence)
        except (TypeError, ValueError):
            log.warning(f"Invalid confidence value: {confidence}, defaulting to 0.6")
            state["intent_confidence"] = 0.6
        state["intent_reason"] = data.get("reason", "")
        state["intent"] = data.get("intent", "simple_query")
        state["intent_confidence"] = float(data.get("confidence", 0.6))
        state["intent_reason"] = data.get("reason", "")
        log.info(f"Intent: {state['intent']}, Confidence: {state['intent_confidence']}, Reason: {state['intent_reason']}")
    except json.JSONDecodeError:
        log.error("Failed to decode LLM response as JSON. Using fallback intent.")
        state["intent"] = "simple_query"
        state["intent_confidence"] = 0.6
        state["intent_reason"] = "fallback"
    except Exception as e:
        log.exception(f"Unexpected error in intent detection: {e}")
        state["intent"] = "simple_query"
        state["intent_confidence"] = 0.6
        state["intent_reason"] = "fallback"
    return state
