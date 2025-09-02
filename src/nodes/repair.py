from typing import Dict, Any
from src.llm.factory import chat_model
from src.prompts import repair as repair_prompt
from src.guardrails.sql_guard import guard_sql
from src.snowflake.client import fetch_all
from tenacity import retry, stop_after_attempt, wait_exponential
from src.prompts.repair_sql import repair_sql_prompt
from src.utils.logging import get_logger    
log = get_logger("repair")


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
def try_repair(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = chat_model(temperature=0.0)
    sql_prompt = repair_sql_prompt.invoke({"sql": state["final_sql"], "error":state.get("last_error", ""), "schema_hint": state.get("schema_hint", "")})
    repaired = llm.invoke(sql_prompt).content.strip() # type: ignore
    print(repaired)
    state["final_sql"] = guard_sql(repaired.replace("```sql","").replace("```",""))
    return state

def run_repair_and_execute(state: Dict[str, Any]) -> Dict[str, Any]:
    state = try_repair(state)
    try:
        cols, rows = fetch_all(state["final_sql"])
        # from src.pii.mask import mask_results
        # rows = mask_results(cols, rows)
        state["columns"] = cols
        state["rows"] = rows
        state["error"] = None
    except Exception as e:
        state["error"] = str(e)
    return state
