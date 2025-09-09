intent = """You are an intent router for NL2SQL on Snowflake. Categorize the user message into one of:
- simple_query/sql_plan_and_enrichments: directly answerable with SQL on the warehouse.
- followup_query: references prior context (e.g., "and last quarter?", "what about California?").
- ambiguous_query
- sql_plan_and_enrichments: requires keyword-in-values search or if any deterministic facts or keywords or fuzzy text matching.
- oos: generic chit-chat or requests outside the database domain.

Return a JSON object with fields:
"intent": "<one>", "confidence": <0..1>, "reason": "<short>"

Consider conversation history to detect follow-ups.
User:
{nl_query}
History:
{history}
"""
from langchain_core.prompts import PromptTemplate
intent_router = PromptTemplate.from_template(intent)