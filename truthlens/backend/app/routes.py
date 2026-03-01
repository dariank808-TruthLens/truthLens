from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional

from backend.logic.utils import make_id, now_iso
from backend.logic.extractors import extract_text
from backend.logic.fallacy_detector import detect_fallacies
from backend.logic.fact_checker import extract_claims, fact_check_claims
from backend.logic.analysis import compute_breakdown

router = APIRouter()

# Supported text-based file types for analysis
ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "docx", "doc", "html", "htm"}


@router.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI backend!"}


@router.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}


@router.post("/analyze")
async def analyze_files(
    files: List[UploadFile] = File(...),
    fact_check: bool = Form(True),
    logical_fallacy_check: bool = Form(True),
    ai_generation_check: bool = Form(False),
):
    """Upload text-based files and run fallacy + fact-check analysis.

    Accepts: .txt, .md, .pdf, .docx, .html
    Returns analysis with fact_checks, fallacies, and credibility breakdown.
    """
    if not files:
        return {"error": "No files provided", "status": 400}

    combined_text = ""
    file_results = []

    for f in files:
        ext = (f.filename or "").rsplit(".", 1)[-1].lower() if "." in (f.filename or "") else ""
        if ext not in ALLOWED_EXTENSIONS:
            file_results.append({"name": f.filename, "skipped": True, "reason": f"Unsupported type .{ext}"})
            continue
        content = await f.read()
        text = extract_text(f.filename or "", content, f.content_type)
        if text:
            combined_text += text + "\n\n"
            file_results.append({"name": f.filename, "chars": len(text)})
        else:
            file_results.append({"name": f.filename, "skipped": True, "reason": "Could not extract text"})

    if not combined_text.strip():
        return {
            "error": "No text could be extracted from the uploaded files",
            "files": file_results,
            "status": 400,
        }

    fact_checks = []
    fallacies = []

    if logical_fallacy_check:
        fallacies = detect_fallacies(combined_text)

    if fact_check:
        claims = extract_claims(combined_text)
        fact_checks = fact_check_claims(claims) if claims else []

    ai_check = {"id": make_id("ai"), "is_ai": False, "score": 0.0, "explanation": "Text-based analysis only; AI check reserved for video."}
    if ai_generation_check:
        ai_check["explanation"] = "AI generation check on text not yet implemented; enable for video later."

    breakdown = compute_breakdown(fact_checks, fallacies, ai_check)

    return {
        "files": file_results,
        "summary": {
            "fact_checks": len(fact_checks),
            "fallacies": len(fallacies),
            "ai_score": ai_check.get("score"),
        },
        "breakdown": breakdown,
        "fact_checks": fact_checks,
        "fallacies": fallacies,
        "ai_check": ai_check,
    }