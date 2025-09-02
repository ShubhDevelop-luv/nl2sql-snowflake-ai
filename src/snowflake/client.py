import snowflake.connector
from typing import Any, List, Dict, Tuple
from src.config import settings
from src.utils.logging import get_logger

log = get_logger("snowflake")

def connect():
    conn = snowflake.connector.connect(
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        account=settings.SNOWFLAKE_ACCOUNT,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
        role=settings.SNOWFLAKE_ROLE,
        client_session_keep_alive=False,
        autocommit=True,
    )
    # Set session-level timeout
    with conn.cursor() as cur:
        cur.execute(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS={settings.STATEMENT_TIMEOUT_SECONDS}")
        cur.execute("ALTER SESSION SET QUERY_TAG='nl2sql_agent'")
    return conn

def fetch_all(sql: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    """
    Executes the given SQL query and returns the column names and all result rows.

    Args:
        sql (str): The SQL query to execute.

    Returns:
        Tuple[List[str], List[Tuple[Any, ...]]]: A tuple containing a list of column names and a list of rows.
    """
    conn = connect()
    try:
        with conn.cursor() as cur:
            log.info("Executing SQL", extra={"sql": sql})
            cur.execute(sql)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()
            return cols, rows # pyright: ignore[reportReturnType]
    finally:
        conn.close()


def get_schema_info() -> List[Tuple[str, str, str, str]]:
    """
    Retrieves schema information for all columns in the specified Snowflake database and schema.

    Returns:
        List[Tuple[str, str, str, str]]: A list of tuples containing table name, column name, data type, and comment.
    """
    # Pull table/column/type/comment from INFORMATION_SCHEMA
    conn = connect()
    try:
        sql = f"""
        SELECT c.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE, c.COMMENT
        FROM {settings.SNOWFLAKE_DATABASE}.INFORMATION_SCHEMA.COLUMNS c
        WHERE c.TABLE_SCHEMA = '{settings.SNOWFLAKE_SCHEMA}'
        AND c.TABLE_NAME IN ('PER_LATEST', 'VELOCITY_ENHANCED_UNLIMITED_LATEST') 
        ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            return list(cur.fetchall()) # type: ignore
    finally:
        conn.close()

def get_tables() -> List[str]:
    conn = connect()
    try:
        sql = f"""
        SELECT TABLE_NAME
        FROM {settings.SNOWFLAKE_DATABASE}.INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{settings.SNOWFLAKE_SCHEMA}'
        AND TABLE_NAME IN ('PER_LATEST', 'VELOCITY_ENHANCED_UNLIMITED_LATEST') 
        ORDER BY TABLE_NAME
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()
        
def get_views() -> List[str]:
    conn = connect()
    try:
        sql = f"""
        SELECT TABLE_NAME
        FROM {settings.SNOWFLAKE_DATABASE}.INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = '{settings.SNOWFLAKE_SCHEMA}'
        AND TABLE_NAME IN ('PER_LATEST', 'VELOCITY_ENHANCED_UNLIMITED_LATEST') 
        ORDER BY TABLE_NAME
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()