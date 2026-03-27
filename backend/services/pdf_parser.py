import io
from pypdf import PdfReader
import re


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file bytes."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def parse_file(file_bytes: bytes, content_type: str, filename: str) -> str:
    """Parse uploaded file to plain text based on content type."""
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return parse_pdf(file_bytes)
    elif content_type == "text/plain" or filename.lower().endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {content_type}. Only PDF and TXT allowed.")


def extract_sections(text: str) -> dict:
    """Extract resume sections using keyword-based detection."""
    sections = {
        "skills": [],
        "experience": [],
        "education": [],
        "summary": "",
    }

    lines = text.split("\n")
    current_section = None
    section_content = []

    # Keyword patterns for section headers
    section_patterns = {
        "skills": r"(?i)^(?:technical\s+)?skills|competencies|technologies|expertise",
        "experience": r"(?i)^(?:work\s+)?experience|employment|professional\s+experience|work\s+history",
        "education": r"(?i)^education|academic|qualifications|degrees",
        "summary": r"(?i)^(?:professional\s+)?summary|objective|profile|about",
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line matches a section header
        matched_section = None
        for section_name, pattern in section_patterns.items():
            if re.match(pattern, line):
                matched_section = section_name
                break

        if matched_section:
            # Save previous section content
            if current_section and section_content:
                if current_section == "summary":
                    sections["summary"] = " ".join(section_content)
                else:
                    sections[current_section] = section_content
            current_section = matched_section
            section_content = []
        elif current_section:
            # Clean bullet points and add content
            cleaned = re.sub(r"^[\u2022\-\*\u25cf\u25cb\u2023\u25aa]\s*", "", line)
            if cleaned:
                section_content.append(cleaned)

    # Save last section
    if current_section and section_content:
        if current_section == "summary":
            sections["summary"] = " ".join(section_content)
        else:
            sections[current_section] = section_content

    # If no summary extracted, use first few lines
    if not sections["summary"]:
        first_lines = [l.strip() for l in lines[:5] if l.strip()]
        sections["summary"] = " ".join(first_lines[:3])

    return sections
