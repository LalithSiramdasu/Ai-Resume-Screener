from langchain_chroma import Chroma
from langchain_core.documents import Document
from services.embeddings import get_embeddings
from config import CHROMA_DIR


# In-memory store for vector store instances per session
_vector_stores: dict[str, Chroma] = {}


def create_vector_store(documents: list[Document], collection_name: str) -> Chroma:
    """Create a ChromaDB vector store from documents.

    Embeds the documents using a local Hugging Face sentence-transformer
    and stores them in a persistent ChromaDB collection.

    Args:
        documents: List of LangChain Document objects to embed and store.
        collection_name: Unique name for the ChromaDB collection (session ID).

    Returns:
        Chroma vector store instance.
    """
    embeddings = get_embeddings()

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_DIR,
    )

    # Cache the vector store instance
    _vector_stores[collection_name] = vector_store

    return vector_store


def get_vector_store(collection_name: str) -> Chroma | None:
    """Retrieve a cached vector store by collection name."""
    if collection_name in _vector_stores:
        return _vector_stores[collection_name]

    # Try to load from persistent storage
    try:
        embeddings = get_embeddings()
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=CHROMA_DIR,
        )
        _vector_stores[collection_name] = vector_store
        return vector_store
    except Exception:
        return None


def search_similar(store: Chroma, query: str, k: int = 4) -> list[Document]:
    """Search vector store for documents similar to query.

    This is the RETRIEVAL step of RAG:
    query → embed → vector search → return relevant chunks.

    Args:
        store: ChromaDB vector store instance.
        query: The search query text.
        k: Number of similar documents to retrieve.

    Returns:
        List of most similar Document objects.
    """
    return store.similarity_search(query, k=k)
