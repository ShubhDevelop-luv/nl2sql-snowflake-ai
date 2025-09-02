from langchain_core.prompts import PromptTemplate

repair_sql = """You are repairing a failing Snowflake SQL while preserving intent.
Inputs:
- Original SQL:
{sql}
- Error Message:
{error}
- Schema hints:
{schema_hint}
Repair the SQL and return ONLY the corrected SQL."""


repair_sql_prompt = PromptTemplate(
    template=repair_sql, 
    input_variables=["sql", "error", "schema_hint"],
)