import json
import re
from collections import Counter
from typing import Iterable

from models.schemas import MatchResult
from config import LLM_MODEL, can_use_groq
from services.llm import chat_completion


MATCH_PROMPT = """You are an expert resume screener and hiring consultant. Analyze the following resume against the job description and provide a detailed assessment.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Respond ONLY with valid JSON in this exact format (no other text, no markdown):
{{
    "score": <integer 0-100 representing match percentage>,
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "gaps": ["<gap 1>", "<gap 2>", "<gap 3>"],
    "insights": ["<insight 1>", "<insight 2>"],
    "assessment": "<2-3 sentence overall assessment>"
}}

Scoring guidelines:
- 90-100: Excellent match, meets all requirements
- 70-89: Good match, meets most requirements
- 50-69: Moderate match, meets some requirements
- 30-49: Weak match, significant gaps
- 0-29: Poor match, minimal relevance

Be specific in strengths, gaps, and insights. Reference actual skills and requirements.
"""


STOPWORDS = {
    "the",
    "and",
    "with",
    "for",
    "that",
    "have",
    "this",
    "from",
    "your",
    "will",
    "are",
    "our",
    "but",
    "not",
    "you",
    "their",
    "about",
    "into",
    "able",
    "over",
}


def _clean_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def _top_keywords(tokens: Iterable[str], limit: int = 10) -> list[str]:
    counter = Counter(tokens)
    return [word for word, _ in counter.most_common(limit)]


def _fallback_match(resume_text: str, jd_text: str) -> MatchResult:
    resume_kw = set(_top_keywords(_clean_tokens(resume_text), 40))
    jd_kw = set(_top_keywords(_clean_tokens(jd_text), 40))

    overlap = list(resume_kw & jd_kw)
    jd_only = list(jd_kw - resume_kw)

    denominator = max(len(jd_kw), 1)
    score = int(round((len(overlap) / denominator) * 100))

    strengths = (
        [f"Resume highlights {kw} which also appears in the job description." for kw in overlap[:3]]
        or ["Resume includes unique strengths even if the JD uses different wording."]
    )
    gaps = (
        [f"JD emphasises {kw} but it was not found in the resume." for kw in jd_only[:3]]
        or ["No obvious skill gaps detected from keyword comparison."]
    )

    if score >= 80:
        assessment = "Resume strongly matches the job description based on overlapping skills."
        insights = ["Most core requirements show direct evidence in the resume."]
    elif score >= 55:
        assessment = "Resume moderately matches the job description with some room for improvement."
        insights = ["Several shared keywords exist but a few requirements need reinforcement."]
    else:
        assessment = "Resume has limited overlap with the job description keywords."
        insights = ["Consider tailoring the resume to highlight more of the JD language."]

    return MatchResult(
        score=max(0, min(100, score)),
        strengths=strengths,
        gaps=gaps,
        insights=insights,
        assessment=assessment,
    )


def calculate_match(resume_text: str, jd_text: str) -> MatchResult:
    """Calculate match score between resume and job description.

    Uses a Groq-hosted Llama 3 model to analyze resume content against job
    requirements and return structured scoring with strengths, gaps, and insights.

    Args:
        resume_text: Full text of the candidate's resume.
        jd_text: Full text of the job description.

    Returns:
        MatchResult with score, strengths, gaps, insights, and assessment.
    """
    prompt = MATCH_PROMPT.format(
        resume_text=resume_text[:4000],  # Limit to avoid token overflow
        jd_text=jd_text[:2000],
    )

    if can_use_groq():
        try:
            response_text = chat_completion(
                [
                    {
                        "role": "system",
                        "content": "You are an expert resume screener who only returns JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=LLM_MODEL,
                temperature=0.2,
                max_tokens=800,
            )

            json_match = re.search(r"\{[\s\S]*\}", response_text)
            if json_match:
                result_data = json.loads(json_match.group())
            else:
                result_data = json.loads(response_text)

            return MatchResult(
                score=max(0, min(100, int(result_data.get("score", 50)))),
                strengths=result_data.get("strengths", [])[:5],
                gaps=result_data.get("gaps", [])[:5],
                insights=result_data.get("insights", [])[:3],
                assessment=result_data.get(
                    "assessment", "Assessment could not be generated."
                ),
            )
        except Exception as err:  # noqa: BLE001
            print(f"Groq match scoring failed, falling back to keyword scoring: {err}")

    return _fallback_match(resume_text, jd_text)
