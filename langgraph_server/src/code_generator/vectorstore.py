import os
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from .document_loader import QuestionModuleDocumentLoader

if __name__ == "__main__":
    print("Adding question data to vectorstore")
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDINGS", ""),
    )

    vector_store = AstraDBVectorStore(
        collection_name="gestalt_module",
        embedding=embeddings,
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT", None),
        token=os.getenv("ASTRA_DB_APPLICATION_TOKEN", None),
        namespace=os.getenv("ASTRA_DB_KEYSPACE", None),
    )

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
    vector_store.add_documents(all_docs)
