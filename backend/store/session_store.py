from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4
from models.schemas import ChatMessage, MatchResult, ResumeData


@dataclass
class SessionData:
    """Stores all session data for a resume screening session."""

    session_id: str
    resume_text: str = ""
    jd_text: str = ""
    resume_data: ResumeData | None = None
    match_result: MatchResult | None = None
    vector_store: Any = None  # Chroma instance
    chat_history: list[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


# In-memory session storage
_sessions: dict[str, SessionData] = {}


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid4())


def create_session(session_id: str, **kwargs) -> SessionData:
    """Create and store a new session.

    Args:
        session_id: Unique session identifier.
        **kwargs: Additional session data fields.

    Returns:
        The created SessionData instance.
    """
    session = SessionData(session_id=session_id, **kwargs)
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> SessionData | None:
    """Retrieve a session by its ID.

    Args:
        session_id: The session identifier.

    Returns:
        SessionData if found, None otherwise.
    """
    return _sessions.get(session_id)


def update_chat_history(session_id: str, message: ChatMessage) -> None:
    """Append a message to the session's chat history.

    Args:
        session_id: The session identifier.
        message: ChatMessage to append.
    """
    session = _sessions.get(session_id)
    if session:
        session.chat_history.append(message)
