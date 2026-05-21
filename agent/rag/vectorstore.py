from typing import Dict, Any, List, Optional
from langchain_community.vectorstores import FAISS

from llm_manager import get_embedding_model
from agent.rag.ehr_to_docs import ehr_to_documents


def build_ehr_vectorstore(ehr: Dict[str, Any]) -> FAISS:
    embedding_model = get_embedding_model()
    docs = ehr_to_documents(ehr)
    return FAISS.from_documents(docs, embedding_model)