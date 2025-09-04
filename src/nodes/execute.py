from typing import Dict, Any
from src.snowflake.client import fetch_all
from src.pii.mask import mask_results

def run_execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        cols, rows = fetch_all(state["final_sql"])
        # rows = mask_results(cols, rows)
        state["columns"] = cols
        state["rows"] = rows
        state["error"] = None
        return state
    except Exception as e:
        state["error"] = str(e)
        return state
