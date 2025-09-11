from typing import List, Tuple, Optional
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from src.llm.factory import embedding_model
from src.utils.logging import get_logger
import os, json


logger = get_logger("schema_index")


def build_schema_docs(info_rows: List[Tuple[str, str, str, str]]) -> List[Document]:
    docs = []
    try:
        for t, c, dtype, comment in info_rows:
            text = (
                f"table: {t}\ncolumn: {c}\ntype: {dtype}\ndescription: {comment or ''}"
            )
            docs.append(Document(page_content=text, metadata={"table": t, "column": c}))
        logger.info("Successfully built schema docs.")
    except Exception as e:
        logger.error(f"Error building schema docs: {e}")
        raise
    return docs


def save_index(docs: List[Document], path: str):
    try:
        embs = embedding_model()
        if embs is None:
            logger.error("Embedding model returned None. Cannot build FAISS index.")
            raise ValueError("Embedding model must not be None.")
        vs = FAISS.from_documents(docs, embs)
        os.makedirs(path, exist_ok=True)
        vs.save_local(path)
        logger.info(f"Index saved successfully at {path}.")
    except Exception as e:
        logger.error(f"Error saving index at {path}: {e}")
        raise


def load_index(path: str):
    try:
        embs = embedding_model()
        if embs is None:
            logger.error("Embedding model returned None. Cannot build FAISS index.")
            raise ValueError("Embedding model must not be None.")
        vs = FAISS.load_local(path, embs, allow_dangerous_deserialization=True)
        logger.info(f"Index loaded successfully from {path}.")
        return vs
    except Exception as e:
        logger.error(f"Error loading index from {path}: {e}")
        raise


def docs_to_schema_hint(docs: List[Document]) -> str:
    seen = set()
    lines = []
    try:
        for d in docs:
            t = d.metadata.get("table")
            c = d.metadata.get("column")
            key = (t, c)
            if key in seen:
                continue
            seen.add(key)
            lines.append(d.page_content)
        logger.info("Schema hint generated successfully.")
    except Exception as e:
        logger.error(f"Error generating schema hint: {e}")
        raise
    return "\n---\n".join(lines)


def retrieve_schema(query: str, k: int = 22, index_path: Optional[str] = None) -> str:
    index_path = index_path or os.getenv("SCHEMA_INDEX_PATH", "./.schema_index")
    try:
        vs = load_index(index_path)
        docs = vs.similarity_search(query, k=k)
        result = docs_to_schema_hint(docs)
        logger.info(f"Schema retrieved successfully for query: {query}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving schema for query '{query}': {e}")
        raise
