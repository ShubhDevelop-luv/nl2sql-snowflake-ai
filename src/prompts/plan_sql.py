from langchain_core.prompts import PromptTemplate

plan_sql = """You are a senior data engineer generating Snowflake SQL. Convert the user request into correct, efficient SQL.
Constraints:
- Use only provided schema hints.
- Avoid SELECT *; select only needed columns.
- Respect filters, time ranges, and aggregations.
- Enrich the sql query
- Keep results human-readable.
Return ONLY the SQL, no explanation.

User request:
{nl_query}

Schema hints:
{schema_hint}

If the request is ambiguous, write a minimal SQL that surfaces key options or ask for a clarifying question (prefixed with "CLARIFY:")."""


plan_sql_prompt = PromptTemplate(
    template=plan_sql, 
    input_variables=["nl_query", "schema_hint"],
)