# scripts/index_schema.py
from src.snowflake.client import get_schema_info
from src.retriever.schema_index import build_schema_docs, save_index
from src.config import settings
from src.utils.logging import get_logger
logger = get_logger("index_schema")

if __name__ == "__main__":
    logger.info("Fetching schema info from Snowflake...")
    rows = get_schema_info()
    logger.info(f"Fetched {len(rows)} columns.")
    docs = build_schema_docs(rows)
    logger.info("Building FAISS index...")
    save_index(docs, settings.SCHEMA_INDEX_PATH)
    logger.info(f"Schema index saved to {settings.SCHEMA_INDEX_PATH}")
