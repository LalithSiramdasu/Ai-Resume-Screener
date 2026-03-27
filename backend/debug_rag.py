import os
from config import CHROMA_DIR
from langchain_chroma import Chroma
from services.embeddings import get_embeddings
from services.rag_chain import ask_with_rag


def debug():
    # Find the latest collection in CHROMA_DIR (they are UUIDs)
    if not os.path.exists(CHROMA_DIR):
        print("CHROMA_DIR does not exist!")
        return

    # Chroma creates SQLite files and folders. Let's just try to instantiate with a known collection?
    # We can't easily list collections in the current LangChain Chroma wrapper without the client.
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collections = client.list_collections()
    if not collections:
        print("No collections in ChromaDB.")
        return

    # Get the name of the last collection
    latest_collection = collections[-1].name
    print(f"Latest collection ID: {latest_collection}")

    store = Chroma(
        collection_name=latest_collection,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )

    # Query for resume chunks
    docs = store.similarity_search("Python React backend experience", k=20)
    print(f"\nRetrieved {len(docs)} documents from resume search:")

    resume_count = 0
    for doc in docs:
        src = doc.metadata.get("source", "unknown")
        if src == "resume":
            resume_count += 1

    print(f"Total Resume Chunks in Search: {resume_count}")

    if resume_count == 0:
        print("CRITICAL: ZERO RESUME CHUNKS WERE FOUND IN THE VECTOR DB!")
    else:
        print("Resume chunks exist. Testing RAG...")
        question = "What are the candidate's strongest technical skills?"
        answer = ask_with_rag(store, question, chat_history=[])
        print("\nRAG Answer:\n", answer)


if __name__ == "__main__":
    debug()
