
from src.pydantic.prompt_validate import enrich_parser
enrichments = """
You are an enrichment extractor for an NL2SQL agent.

User query:
{nl_query}

From the user query, extract:
- deterministic facts (explicit numbers, dates, ranges)
- keywords (domain terms, product names, categories)
- geography (city/state/country; if city/state without country, infer if possible)
- industry codes (NAICS/SIC) only if explicitly mentioned
- action type: add, narrow, switch, remove, reset

Rules:
- Keywords-only queries are valid and generate SQL.
- Enrichments persist until canceled.
- Never treat enrichment outputs as filters.
- Geography: if missing country, infer or ask.
- Preserve AND/OR/NOT and grouping in plain English.

Return JSON with keys: deterministic, keywords, geography, industry_codes, action.
"""

from langchain_core.prompts import PromptTemplate

enrichment_prompt = PromptTemplate(
    template=enrichments, 
    input_variables=["nl_query"], 
    partial_variables={"format_instructions": enrich_parser.get_format_instructions()}
)