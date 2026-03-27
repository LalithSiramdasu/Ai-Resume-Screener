from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse, ChatMessage
from services.rag_chain import ask_with_rag
from store.session_store import get_session, update_chat_history

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """RAG-powered chat endpoint.

    This endpoint implements the full RAG pipeline:
    1. Receive question + session ID
    2. Retrieve vector store from session
    3. Embed question → search ChromaDB → retrieve relevant chunks
    4. Pass context + question + chat history to the LLM
    5. Return AI answer with updated chat history

    NOT a direct LLM query — uses actual RAG retrieval.
    """
    # Get session
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {request.session_id}. Please upload files first.",
        )

    if not session.vector_store:
        raise HTTPException(
            status_code=400,
            detail="No vector store found for this session. Please re-upload files.",
        )

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Execute RAG pipeline: embed → search → retrieve → generate
        answer = ask_with_rag(
            store=session.vector_store,
            question=question,
            chat_history=session.chat_history,
            jd_text=session.jd_text,
        )

        # Update chat history with user question and AI answer
        user_msg = ChatMessage(role="user", content=question)
        assistant_msg = ChatMessage(role="assistant", content=answer)

        update_chat_history(request.session_id, user_msg)
        update_chat_history(request.session_id, assistant_msg)

        return ChatResponse(
            answer=answer,
            chat_history=session.chat_history,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}",
        )
