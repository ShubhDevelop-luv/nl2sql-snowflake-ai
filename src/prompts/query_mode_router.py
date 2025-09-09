from langchain_core.prompts import PromptTemplate
from typing import Literal  
from src.pydantic.prompt_validate import query_model

query_mode_router = """
You are a query mode classifier for NL2SQL.
Given the user request, decide if it is:
- Plan_SQL: Only needs SQL results from Snowflake.
- SQL_PLAN_AND_ENRICHMENTS: Needs SQL results plus additional enrichment attributes.

Return JSON:
`
  "query_mode": "<Plan_SQL|SQL_PLAN_AND_ENRICHMENTS>",
  "reason": "<short reason>"
`

User request: {nl_query}
"""



enrichment_prompt = PromptTemplate(
    template=query_mode_router, 
    input_variables=["nl_query"], 
    partial_variables={"format_instructions": query_model.get_format_instructions()}
)