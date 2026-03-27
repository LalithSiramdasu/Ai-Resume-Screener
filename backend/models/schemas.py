from pydantic import BaseModel, Field
from typing import Literal


class ResumeData(BaseModel):
    raw_text: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    summary: str = ""


class MatchResult(BaseModel):
    score: int = 0
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)
    assessment: str = ""


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    session_id: str
    question: str


class UploadResponse(BaseModel):
    session_id: str
    match_result: MatchResult
    resume_data: ResumeData


class ChatResponse(BaseModel):
    answer: str
    chat_history: list[ChatMessage] = Field(default_factory=list)
