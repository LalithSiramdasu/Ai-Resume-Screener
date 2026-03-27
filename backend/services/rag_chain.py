from langchain_chroma import Chroma
from textwrap import shorten

from services.vector_store import search_similar
from models.schemas import ChatMessage
from config import LLM_MODEL, can_use_groq
from services.llm import chat_completion


# System prompt for the RAG assistant
SYSTEM_PROMPT = """You are a professional Resume Screening Assistant. Your role is to answer questions about a candidate's resume and evaluate their fit against a provided job description.

IMPORTANT RULES:
1. The resume context below was retrieved from a vector search over the candidate's resume. Treat it as the primary evidence.
2. The job description is provided separately so you can compare the candidate against the role when needed.
3. ONLY answer based on the retrieved resume context, the job description, and the conversation history.
4. If the answer is not supported by the retrieved resume context, clearly say that it is not available in the provided resume.
5. When comparing fit against the role, be objective and point to matching or missing evidence from the retrieved resume context.
6. Provide concise but specific answers.

RETRIEVED RESUME CONTEXT:
{resume_context}

JOB DESCRIPTION REFERENCE:
{job_description}

CONVERSATION HISTORY:
{chat_history}
"""


def _format_chat_history(history: list[ChatMessage]) -> str:
    """Format chat history for context injection."""
    if not history:
        return "No previous conversation."

    formatted = []
    for msg in history[-6:]:  # Keep last 6 messages for context
        role = "Human" if msg.role == "user" else "Assistant"
        formatted.append(f"{role}: {msg.content}")

    return "\n".join(formatted)


def _format_context(documents) -> str:
    """Format retrieved documents into context string."""
    if not documents:
        return "No relevant resume context found."

    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(f"--- [RESUME CHUNK {i}] ---\n{doc.page_content}")

    return "\n\n".join(context_parts)


def _format_job_description(jd_text: str) -> str:
    if not jd_text.strip():
        return "No job description was provided for this session."

    return jd_text[:2500]


def _local_answer(question: str, relevant_docs, jd_text: str) -> str:
    if not relevant_docs:
        return "I could not find any resume snippets related to that question."

    snippets = []
    for doc in relevant_docs[:3]:
        snippet = shorten(doc.page_content.strip().replace("\n", " "), width=260, placeholder="...")
        snippets.append(f"- {snippet}")

    response = [
        "Here is what the resume mentions:",
        *snippets,
    ]
    if jd_text.strip():
        response.append("The job description reference is available for comparison but no full LLM analysis was run.")
    response.append(
        "(Groq LLM is unavailable, so this answer is based on retrieved resume text only.)"
    )
    return "\n".join(response)


def ask_with_rag(
    store: Chroma,
    question: str,
    chat_history: list[ChatMessage],
    jd_text: str = "",
) -> str:
    """Answer a question using the RAG pipeline.

    This is the COMPLETE RAG flow:
    1. Embed the question (done inside similarity_search)
    2. Search ChromaDB for relevant resume chunks
    3. Format retrieved chunks as context
    4. Send retrieved resume context + job description + question + chat history to the LLM
    5. Return the LLM's context-aware response

    Args:
        store: ChromaDB vector store with resume embeddings.
        question: User's question about the resume.
        chat_history: Previous conversation messages for context.
        jd_text: Job description text for role-fit comparisons.

    Returns:
        AI-generated answer based on retrieved resume context.
    """
    # Step 1 & 2: Embed question → Search similar chunks in ChromaDB
    relevant_docs = search_similar(store, question, k=8)

    # Step 3: Format retrieved context
    resume_context = _format_context(relevant_docs)

    # Step 4: Build the augmented prompt
    history_str = _format_chat_history(chat_history)

    prompt = SYSTEM_PROMPT.format(
        resume_context=resume_context,
        job_description=_format_job_description(jd_text),
        chat_history=history_str,
    )

    if can_use_groq():
        try:
            return chat_completion(
                [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": question},
                ],
                model=LLM_MODEL,
                temperature=0.3,
                max_tokens=900,
            )
        except Exception as err:  # noqa: BLE001
            print(f"Groq chat failed, using local snippets instead: {err}")

    return _local_answer(question, relevant_docs, jd_text)
