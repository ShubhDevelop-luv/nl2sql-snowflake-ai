from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser

class intent(BaseModel):
    intent: str
    confidence: float
    reason: str

class clarify(BaseModel):
    clarifying_question: str

class rewritten(BaseModel):
    nl_query_effective: str

intent_parser = JsonOutputParser(pydantic_object=intent)
clarify_parser = JsonOutputParser(pydantic_object=clarify)
rewritten_parser = JsonOutputParser(pydantic_object=rewritten)

