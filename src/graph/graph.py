from typing import TypedDict, List, Any, Dict
from langgraph.graph import StateGraph, END
from src.nodes.intent import run_intent
from src.nodes.clarify import run_clarify
from src.nodes.enrich import run_extract_enrichments
from src.nodes.followup import run_followup_rewrite
from src.nodes.plan import run_plan_sql
from src.nodes.validate import run_validate_sql
from src.nodes.execute import run_execute
from src.nodes.repair import run_repair_and_execute
from src.nodes.respond import run_respond
from src.nodes.plan_with_enrichments import run_plan_with_enrichments  



class AgentState(TypedDict, total=False):
    session_id: str
    nl_query: str
    nl_query_effective: str
    history_text: str
    intent: str
    intent_confidence: float
    intent_reason: str
    schema_hint: str
    proposed_sql: str
    final_sql: str
    columns: List[str]
    rows: List[Any]
    error: str
    clarifying_question: str
    awaiting_clarification: bool

def _route_after_intent(state: AgentState):
    intent = state.get("intent", "simple_query")
    conf = float(state.get("intent_confidence", 0.6))
    if intent == "ambiguous_query" or conf < 0.65:
        return "clarify"
    if intent == "followup_query":
        return "followup"
    if intent == "sql_plan_and_enrichments":
        return "extract_enrichments"
    if intent in ("oos",):
        return "respond"
    return "plan"

def _route_after_enrich(state: AgentState):
    """
    If enrichments exist after extraction, go to enrichment planner
    If no enrichments but some keywords/deterministic, go to normal planner
    If no enrichments and no keywords/deterministic, clarify
    """
    try:
        if state.get("enrichment_active"):
            return "plan_with_enrichments"
        # If no usable filters/keywords, clarify
        if not state.get("keywords") and not state.get("deterministic"):
            state["awaiting_clarification"] = True
            return "respond"
        return "plan"
    except Exception:
        state["error"] = "Error determining enrichment routing"
        return "respond"


def _route_after_validate(state: AgentState):
    if state.get("awaiting_clarification"):
        return "respond"
    return "execute"

def _route_after_execute(state: AgentState):
    if state.get("error"):
        return "repair"
    return "respond"

def _route_after_repair(state: AgentState):
    if state.get("error"):
        return "respond"
    return "respond"

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("intent", run_intent) # type: ignore
    g.add_node("clarify", run_clarify) # type: ignore
    g.add_node("followup", run_followup_rewrite) # type: ignore
    g.add_node("plan", run_plan_sql) # type: ignore
    g.add_node("plan_with_enrichments", run_plan_with_enrichments) # type: ignore
    g.add_node("validate", run_validate_sql) # type: ignore
    g.add_node("execute", run_execute) # type: ignore
    g.add_node("repair", run_repair_and_execute) # type: ignore
    g.add_node("respond", run_respond) # type: ignore

    g.set_entry_point("intent")

    g.add_conditional_edges("intent", _route_after_intent, {
        "clarify": "clarify",
        "followup": "followup",
        "extract_enrichments": "extract_enrichments",
        "plan": "plan",
        "respond": "respond",
    })

    g.add_conditional_edges("extract_enrichments", _route_after_enrich, {
        "plan_with_enrichments": "plan_with_enrichments",
        "plan": "plan",
        "respond": "respond"
    })

    g.add_edge("followup", "plan")
    g.add_edge("plan", "validate")
    g.add_edge("plan_with_enrichments", "validate")

    g.add_conditional_edges("validate", _route_after_validate, {
        "execute": "execute",
        "respond": "respond"
    })

    g.add_conditional_edges("execute", _route_after_execute, {
        "repair": "repair",
        "respond": "respond"
    })

    g.add_conditional_edges("repair", _route_after_repair, {
        "respond": "respond"
    })

    g.add_edge("respond", END)
    return g.compile()
