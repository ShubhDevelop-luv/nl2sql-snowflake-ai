from pydantic import BaseModel, Field
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


enrich_parser = JsonOutputParser(pydantic_object=EnrichmentExtraction)
intent_parser = JsonOutputParser(pydantic_object=intent)
clarify_parser = JsonOutputParser(pydantic_object=clarify)
rewritten_parser = JsonOutputParser(pydantic_object=rewritten)

