from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, source: str = "document") -> list[Document]:
    """Split text into chunks for embedding and vector storage.

    Args:
        text: The raw text to split into chunks.
        source: A label for the source metadata (for this project, usually 'resume').

    Returns:
        List of LangChain Document objects with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    documents = splitter.create_documents(
        texts=[text],
        metadatas=[{"source": source}],
    )

    return documents
