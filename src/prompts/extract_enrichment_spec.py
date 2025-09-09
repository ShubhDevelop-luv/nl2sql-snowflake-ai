from langchain.prompts import PromptTemplate
from src.pydantic.prompt_validate import enrichment_response

extract_enrichment_spec = PromptTemplate(
    input_variables=["nl_query"],
    partial_variables={"format_instructions": enrichment_response.get_format_instructions()},
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

Rules:
Return one JSON object with exactly TWO keys:
<insights_spec.name> → the value  
source_<insights_spec.name> → a short provenance note  

Follow insights_spec.instruction precisely for the value.  
Numbers → JSON number. Dates → ISO string YYYY-MM-DD. Text → JSON string.  
Prefer the most recent official or primary source. If multiple, choose the newest credible one.  
Include the year and month of the source information if possible.  
No extra keys. No commentary beyond the provenance note.  
Return null only if you can’t find anything. It is better to return some value than nothing.  

Provenance note (source_):  
A concise string ≤ 480 chars that names the best verification locus (e.g., “2024 annual report,” “state DOH hospital profile,” “company careers page,” “10-K Item 1,” “press release on YYYY-MM-DD”).  
If you know the specific document type and date, include them. If uncertain, name the best category (e.g., “latest audited financials”).  
Do NOT invent URLs or document titles. Only include a URL if it is explicitly provided in the input.  
Do NOT mention “training data,” models, prompts, or internal reasoning.  
User request: {nl_query}
"""
)