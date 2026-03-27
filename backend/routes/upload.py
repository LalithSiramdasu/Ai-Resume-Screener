from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import UploadResponse, ResumeData, MatchResult
from services.pdf_parser import parse_file, extract_sections
from services.chunker import chunk_text
from services.vector_store import create_vector_store
from services.match_scorer import calculate_match
from store.session_store import generate_session_id, create_session

router = APIRouter(prefix="/api", tags=["Upload"])

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
ALLOWED_CONTENT_TYPES = {"application/pdf", "text/plain", "application/octet-stream"}


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file type."""
    filename = (file.filename or "").strip()
    content_type = (file.content_type or "").lower()

    if not filename or "." not in filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded files must include a .pdf or .txt filename.",
        )

    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {extension}. Only PDF and TXT files are allowed.",
        )

    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid content type: {content_type}. Only PDF and TXT files are allowed."
            ),
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_files(
    resume: UploadFile = File(..., description="Resume file (PDF or TXT)"),
    job_description: UploadFile = File(
        ..., description="Job Description file (PDF or TXT)"
    ),
):
    """Upload resume and job description for analysis.

    This endpoint:
    1. Validates and parses both files to plain text
    2. Extracts resume sections (Skills, Experience, Education, Summary)
    3. Chunks the resume text for embedding
    4. Creates vector embeddings and stores the resume chunks in ChromaDB
    5. Calculates match score between resume and JD
    6. Returns session ID + match results + resume data
    """
    # Validate file types
    validate_file(resume)
    validate_file(job_description)

    try:
        # Read file contents
        resume_bytes = await resume.read()
        jd_bytes = await job_description.read()

        # Parse files to text
        resume_text = parse_file(
            resume_bytes,
            resume.content_type or "",
            resume.filename or "resume.txt",
        )
        jd_text = parse_file(
            jd_bytes,
            job_description.content_type or "",
            job_description.filename or "jd.txt",
        )

        if not resume_text.strip():
            raise HTTPException(
                status_code=400, detail="Resume file is empty or could not be read."
            )
        if not jd_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description file is empty or could not be read.",
            )

        # Extract resume sections
        sections = extract_sections(resume_text)
        resume_data = ResumeData(
            raw_text=resume_text,
            skills=sections.get("skills", []),
            experience=sections.get("experience", []),
            education=sections.get("education", []),
            summary=sections.get("summary", ""),
        )

        # Chunk resume text for RAG retrieval
        resume_chunks = chunk_text(resume_text, source="resume")

        # Generate session ID
        session_id = generate_session_id()

        # Create vector store with resume embeddings only
        vector_store = create_vector_store(
            documents=resume_chunks,
            collection_name=session_id,
        )

        # Calculate match score
        match_result = calculate_match(resume_text, jd_text)

        # Store session data
        create_session(
            session_id=session_id,
            resume_text=resume_text,
            jd_text=jd_text,
            resume_data=resume_data,
            match_result=match_result,
            vector_store=vector_store,
        )

        return UploadResponse(
            session_id=session_id,
            match_result=match_result,
            resume_data=resume_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
