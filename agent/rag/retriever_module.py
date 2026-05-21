from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def retrieve_ehr_context(
    vector_store: FAISS,
    query: str,
    k: int = 6
):
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)

    if isinstance(docs, Document):
        return [docs]
    return list(docs)