from langchain.prompts import PromptTemplate
from src.pydantic.prompt_validate import enrichment_response

extract_enrichment_spec = PromptTemplate(
    input_variables=["nl_query"],
    partial_variables={
        "format_instructions": enrichment_response.get_format_instructions()
    },
    template="""
You are an enrichment spec extractor.
From the user request, extract the enrichment attribute name and a short instruction.

Return JSON:
{{
  "insights_spec": {{
    "name": "<snake_case_attribute_name>",
    "instruction": "<clear instruction>"
  }}
}}

User request: {nl_query}
""",
)
