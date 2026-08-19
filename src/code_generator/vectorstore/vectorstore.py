from functools import lru_cache
from typing import Any

from langchain_astradb import AstraDBVectorStore
from src.core.settings import get_settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from .document_loader import QuestionModuleDocumentLoader


@lru_cache
def get_vector_store() -> AstraDBVectorStore:
    settings = get_settings()

    if not settings.ASTRA_DB_API_ENDPOINT:
        raise RuntimeError("Missing ASTRA_DB_API_ENDPOINT")
    if not settings.ASTRA_DB_APPLICATION_TOKEN:
        raise RuntimeError("Missing ASTRA_DB_APPLICATION_TOKEN")

    embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)

    return AstraDBVectorStore(
        collection_name="gestalt_module",
        embedding=embeddings,
        api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
        token=settings.ASTRA_DB_APPLICATION_TOKEN,
    )


class LazyVectorStore:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_vector_store(), name)


vector_store = LazyVectorStore()

if __name__ == "__main__":
    vector_store = get_vector_store()
    print("Extracting Code Examples")
    example_pairs = [
        ("question", "question.html"),
        ("question.html", "server.js"),
        ("question.html", "server.py"),
        ("question.html", "solution.html"),
    ]
    all_docs = []
    for inp, out in example_pairs:
        all_docs.extend(
            QuestionModuleDocumentLoader(input_col=inp, output_col=out).load()
        )
    if not all_docs:
        raise ValueError("No documents loaded from example_pairs.")
    print(f"Total Documents {len(all_docs)}\n First Doc Example {all_docs[0]}")

    vector_store.add_documents(all_docs)
