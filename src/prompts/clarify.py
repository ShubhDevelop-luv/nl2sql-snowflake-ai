from langchain_core.prompts import PromptTemplate
from src.pydantic.prompt_validate import clarify_parser

clarify = """Craft a single, concise clarifying question that will resolve the ambiguity in the user's request.
{format_instructions}
User:
{nl_query}
History:
{history}
Return ONLY the question."""

clarify_prompt = PromptTemplate(
    template=clarify, 
    input_variables=["nl_query", "history"], 
    partial_variables={"format_instructions": clarify_parser.get_format_instructions()}
)