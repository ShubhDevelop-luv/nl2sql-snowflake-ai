from src.retriever.schema_index import retrieve_schema
from src.utils.logging import get_logger
logger = get_logger("retrieve")

def get_relevant_schema_hint(nl_query: str) -> str:
    try:
        return retrieve_schema(nl_query, k=12)
    except Exception as e:
        logger.error(f"Error retrieving schema hint: {e}")
        return ""