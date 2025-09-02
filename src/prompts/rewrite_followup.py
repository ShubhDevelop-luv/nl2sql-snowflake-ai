from langchain_core.prompts import PromptTemplate
from src.pydantic.prompt_validate import rewritten_parser

rewrite= """Rewrite the user's follow-up into a standalone request using prior messages.
{format_instructions}
History:
{history}
Follow-up:
{followup}
Return ONLY the rewritten standalone request."""

rewrite_followup = PromptTemplate(
    template=rewrite, 
    input_variables=["followup", "history"], 
    partial_variables={"format_instructions": rewritten_parser.get_format_instructions()}
)