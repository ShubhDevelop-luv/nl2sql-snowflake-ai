from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.config import settings

def chat_model(model: Optional[str] = None, temperature: float = 0.1):
    try:
        return ChatOpenAI(
            model=model or settings.AZURE_OPENAI_DEPLOYMENT_NAME or "gpt-4o-mini",
            temperature=temperature,
            timeout=30,
        )
    except Exception as e:
        # Log or handle the error as needed
        print(f"Error initializing ChatOpenAI: {e}")
        return None

def embedding_model():
    try:
        return OpenAIEmbeddings(
            model=settings.AZURE_OPENAI_EMBED_DEPLOYMENT or "text-embedding-3-small"
        )
    except Exception as e:
        # Log or handle the error as needed
        print(f"Error initializing OpenAIEmbeddings: {e}")
        return None
