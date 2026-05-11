from langchain_astradb import AstraDBVectorStore
from src.core.settings import get_settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from .document_loader import QuestionModuleDocumentLoader

settings = get_settings()
embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)


vector_store = AstraDBVectorStore(
    collection_name="gestalt_module",
    embedding=embeddings,
    api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
    token=settings.ASTRA_DB_APPLICATION_TOKEN,
)

if __name__ == "__main__":
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
