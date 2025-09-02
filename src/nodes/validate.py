from typing import Dict, Any
from src.guardrails.sql_guard import guard_sql, clean_sql_query
from src.utils.logging import get_logger    
log = get_logger("validate")

def run_validate_sql(state: Dict[str, Any]) -> Dict[str, Any]:
    sql = state["proposed_sql"]
    if sql.upper().startswith("CLARIFY:"):
        state["clarifying_question"] = sql.replace("CLARIFY:", "").replace("```sql","").strip()
        state["awaiting_clarification"] = True
        print(state)
        return state
    final_sql = guard_sql(clean_sql_query(sql))
    state["final_sql"] = final_sql
    return state
