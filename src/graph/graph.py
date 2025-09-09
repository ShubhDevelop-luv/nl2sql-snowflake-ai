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
from src.nodes.plan_with_enrichments import run_enrichment
from src.nodes.extract_enrichment_spec import run_extract_enrichment_spec
from src.nodes.query_mode import run_query_mode
from src.utils.logging import get_logger

log = get_logger("graph")


class AgentState(TypedDict, total=False):
    # Session metadata
    session_id: str
    nl_query: str
    nl_query_effective: str
    history_text: str

    # Intent classification
    intent: str
    intent_confidence: float
    intent_reason: str

    # Query mode classification
    query_mode: str  # "Plan_SQL" or "SQL_PLAN_AND_ENRICHMENTS"
    query_mode_reason: str

    # SQL planning
    # schema_hint: str
    plan_sql_context: str
    proposed_sql: str
    final_sql: str

    # Execution results
    columns: List[str]
    rows: List[Any]
    error: str

    # Clarification
    clarifying_question: str
    awaiting_clarification: bool

    # Enrichment
    insights_spec: Dict[str, Any]
    enrichment_items: List[Dict[str, Any]]
    enriched_rows: List[Dict[str, Any]]
    enrichment_errors: int

    # Response shaping
    search_summary: Dict[str, Any]


def _route_after_intent(state: AgentState):
    intent = state.get("intent", "simple_query")
    conf = float(state.get("intent_confidence", 0.6))
    if intent == "ambiguous_query" or conf < 0.65:
        return "clarify"
    if intent == "followup_query":
        return "followup"
    if intent == "sql_plan_and_enrichments":
        return "plan"
    if intent in ("oos",):
        return "respond"
    return "plan"


def _route_after_validate(state: AgentState):
    if state.get("awaiting_clarification"):
        return "respond"
    return "execute"


def _route_after_execute(state: AgentState):
    if state.get("error"):
        return "repair"
    if state.get("query_mode") == "SQL_PLAN_AND_ENRICHMENTS":
        log.info("Routing to extract_enrichment_spec based on query_mode")
        return "extract_enrichment_spec"
    log.info("Routing to respond")
    return "respond"


def _route_after_repair(state: AgentState):
    if state.get("error"):
        return "respond"
    return "respond"


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("intent", run_intent)  # type: ignore
    g.add_node("query_mode", run_query_mode)  # type: ignore
    g.add_node("clarify", run_clarify)  # type: ignore
    g.add_node("followup", run_followup_rewrite)  # type: ignore
    g.add_node("plan", run_plan_sql)  # type: ignore
    g.add_node("validate", run_validate_sql)  # type: ignore
    g.add_node("execute", run_execute)  # type: ignore
    g.add_node("repair", run_repair_and_execute)  # type: ignore
    g.add_node("respond", run_respond)  # type: ignore
    # New enrichment nodes
    g.add_node("extract_enrichment_spec", run_extract_enrichment_spec)  # type: ignore
    g.add_node("run_enrichment", run_enrichment)  # type: ignore

    g.set_entry_point("intent")

    g.add_conditional_edges(
        "intent",
        _route_after_intent,
        {
            "clarify": "clarify",
            "followup": "followup",
            "plan": "query_mode",
            "respond": "respond",
        },
    )

    g.add_edge("followup", "query_mode")
    g.add_edge("query_mode", "plan")
    g.add_edge("plan", "validate")
    g.add_conditional_edges(
        "validate", _route_after_validate, {"execute": "execute", "respond": "respond"}
    )

    # Advanced execute routing
    g.add_conditional_edges(
        "execute",
        _route_after_execute,
        {
            "repair": "repair",
            "extract_enrichment_spec": "extract_enrichment_spec",
            "respond": "respond",
        },
    )

    # Enrichment branch
    g.add_edge("extract_enrichment_spec", "run_enrichment")
    g.add_edge("run_enrichment", "respond")
    g.add_edge("clarify", "respond")
    g.add_conditional_edges("repair", _route_after_repair, {"respond": "respond"})

    g.add_edge("respond", END)
    return g.compile()
