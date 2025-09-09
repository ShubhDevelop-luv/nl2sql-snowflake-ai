from pydantic import BaseModel, Field, constr
from typing import Literal, Any, Dict
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser

class intent(BaseModel):
    intent: str
    confidence: float
    reason: str

class clarify(BaseModel):
    clarifying_question: str

class rewritten(BaseModel):
    nl_query_effective: str


class EnrichmentExtraction(BaseModel):
    deterministic: dict = Field(default_factory=dict)
    keywords: list[str] = Field(default_factory=list)
    geography: dict = Field(default_factory=dict)
    industry_codes: list[str] = Field(default_factory=list)
    action: str = Field(default="add")

class QueryModel(BaseModel):  
    query_mode: Literal["Plan_SQL", "SQL_PLAN_AND_ENRICHMENTS"]  
    reason: str = Field(..., min_length=1, description="A short reason for the query")


class InsightsSpec(BaseModel):
    name: constr(pattern="^[a-z0-9_]+$") = Field(..., description="Snake_case attribute name")  # type: ignore
    instruction: str = Field(..., min_length=1, description="Clear instruction for enrichment")

class EnrichmentResponse(BaseModel):
    insights_spec: InsightsSpec


from pydantic import BaseModel, Field, constr
from typing import Optional, Union

class EnrichmentLLMResponse(BaseModel):
    # Dynamic field name will be injected at runtime
    value: Union[str, float, int, None] = Field(None, description="Extracted enrichment value")
    source: Optional[str] = Field(None, description="Provenance note ≤ 480 chars")

    @classmethod
    def from_llm_json(cls, data: dict, spec_name: str):
        expected_value_key = spec_name
        expected_source_key = f"source_{spec_name}"

        if expected_value_key not in data or expected_source_key not in data:
            raise ValueError(f"Missing required keys: {expected_value_key}, {expected_source_key}")

        return cls(
            value=data[expected_value_key],
            source=data[expected_source_key]
        )


query_model = JsonOutputParser(pydantic_object=QueryModel)
enrich_parser = JsonOutputParser(pydantic_object=EnrichmentExtraction)
intent_parser = JsonOutputParser(pydantic_object=intent)
clarify_parser = JsonOutputParser(pydantic_object=clarify)
rewritten_parser = JsonOutputParser(pydantic_object=rewritten)
enrichment_response = JsonOutputParser(pydantic_object=EnrichmentResponse)
enrichment_LLM_response = JsonOutputParser(pydantic_object=EnrichmentLLMResponse)
    

