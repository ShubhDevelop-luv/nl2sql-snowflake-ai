from typing import Tuple
import sqlglot
from sqlglot import exp
from src.config import settings
from src.utils.logging import get_logger
logger = get_logger("sql_guard")

READ_ONLY_ERROR = "Only SELECT queries are allowed."

SENSITIVE_COLUMNS = {"email", "phone", "ssn", "credit_card", "pan", "aadhaar", "password"}

def ensure_select_only(sql: str) -> None:
    parsed = sqlglot.parse_one(sql, read="snowflake")
    if not isinstance(parsed, exp.Select) and not isinstance(parsed, exp.Union) and not isinstance(parsed, exp.With):
        logger.error(f"Rejected non-SELECT query: {sql}")
        raise ValueError(READ_ONLY_ERROR)
    logger.debug("Query passed SELECT-only check.")

def enforce_limit(sql: str, default_limit: int, hard_cap: int) -> str:
    try:
        parsed = sqlglot.parse_one(sql, read="snowflake")
        # Add LIMIT if none
        has_limit = any(isinstance(node, exp.Limit) for node in parsed.find_all(exp.Limit))
        if not has_limit:
            logger.info(f"No LIMIT found in query. Adding default LIMIT {default_limit}.")
            parsed = exp.select("*").from_(parsed.subquery("sub")).limit(default_limit) # type: ignore
        # Cap any existing limit
        for node in parsed.find_all(exp.Limit):
            lit = node.this
            if isinstance(lit, exp.Literal) and lit.is_number:
                val = int(lit.this)
                if val > hard_cap:
                    logger.warning(f"LIMIT {val} exceeds hard cap {hard_cap}. Capping to {hard_cap}.")
                    node.this = exp.Literal.number(hard_cap) # type: ignore
        return parsed.sql(dialect="snowflake")
    except Exception as e:
        logger.error(f"Error enforcing LIMIT on query: {sql}. Exception: {e}")
        # Best-effort fallback
        return f"SELECT * FROM ({sql}) AS sub LIMIT {default_limit}"

def check_sensitive_columns(sql: str) -> None:
    lowered = sql.lower()
    hits = [sc for sc in SENSITIVE_COLUMNS if f".{sc}" in lowered or f" {sc}" in lowered]
    if hits:
        logger.info(f"Sensitive columns detected in query: {hits}. Query: {sql}")
        # Allowed to query but will be masked later; log only

def guard_sql(sql: str) -> str:
    logger.debug(f"Guarding SQL query: {sql}")
    ensure_select_only(sql)
    check_sensitive_columns(sql)
    sql_limited = enforce_limit(sql, settings.DEFAULT_LIMIT, settings.HARD_ROW_CAP)
    logger.debug(f"Final guarded SQL: {sql_limited}")
    return sql_limited

import re

def clean_sql_query(text: str) -> str:
    """
    Clean SQL query by removing code block syntax, various SQL tags, backticks,
    prefixes, and unnecessary whitespace while preserving the core SQL query.

    Args:
        text (str): Raw SQL query text that may contain code blocks, tags, and backticks

    Returns:
        str: Cleaned SQL query
    """
    # Step 1: Remove code block syntax and any SQL-related tags
    # This handles variations like ```sql, ```SQL, ```SQLQuery, etc.
    block_pattern = r"```(?:sql|SQL|SQLQuery|mysql|postgresql)?\s*(.*?)\s*```"
    text = re.sub(block_pattern, r"\1", text, flags=re.DOTALL)

    # Step 2: Handle "SQLQuery:" prefix and similar variations
    # This will match patterns like "SQLQuery:", "SQL Query:", "MySQL:", etc.
    prefix_pattern = r"^(?:SQL\s*Query|SQLQuery|MySQL|PostgreSQL|SQL)\s*:\s*"
    text = re.sub(prefix_pattern, "", text, flags=re.IGNORECASE)

    # Step 3: Extract the first SQL statement if there's random text after it
    # Look for a complete SQL statement ending with semicolon
    sql_statement_pattern = r"(SELECT.*?;)"
    sql_match = re.search(sql_statement_pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if sql_match:
        text = sql_match.group(1)

    # Step 4: Remove backticks around identifiers
    text = re.sub(r'`([^`]*)`', r'\1', text)

    # Step 5: Normalize whitespace
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)

    # Step 6: Preserve newlines for main SQL keywords to maintain readability
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY',
               'LIMIT', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN',
               'OUTER JOIN', 'UNION', 'VALUES', 'INSERT', 'UPDATE', 'DELETE']

    # Case-insensitive replacement for keywords
    pattern = '|'.join(r'\b{}\b'.format(k) for k in keywords)
    text = re.sub(f'({pattern})', r'\n\1', text, flags=re.IGNORECASE)

    # Step 7: Final cleanup
    # Remove leading/trailing whitespace and extra newlines
    text = text.strip()
    text = re.sub(r'\n\s*\n', '\n', text)

    return text
