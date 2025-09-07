


plan_sql_with_enrichments = """
You are a senior data engineer generating Snowflake SQL with enrichment context.

User request:
{nl_query}

Enrichments (persisted context):
{enrichments}

Schema hints:
{schema_hint}

Rules:
- Keywords-only queries are valid and generate SQL.
- Enrichments persist until canceled.
- Never treat enrichment outputs as filters.
- Geography: if city/state without country, infer or ask.
- Industry codes only if explicitly requested.
- Preserve AND/OR/NOT and grouping in plain English in verbalization.
- Respect filters, time ranges, and aggregations from the NL query.
- Avoid SELECT *; select only needed columns.
- Prefer explicit JOINs with ON keys inferred from names.

Return ONLY the SQL, no explanation.
"""


from langchain_core.prompts import PromptTemplate
plan_sql_with_enrichments_router = PromptTemplate.from_template(plan_sql_with_enrichments)