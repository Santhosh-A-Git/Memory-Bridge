# pyrefly: ignore [missing-import]
from fastapi import APIRouter
# pyrefly: ignore [missing-import]
from app.models.schemas import (
    MemoryParseRequest, MemoryParseResponse,
    CandidateRequest, CandidateResponse, CandidateResult,
    NextClueRequest, NextClueResponse, SessionEventRequest
)
from app.services.gemini import parse_memory_with_gemini, get_next_clue_with_gemini
from app.retrieval.search import get_candidates, extract_available_clues

router = APIRouter()

@router.post("/memory/parse", response_model=MemoryParseResponse)
def parse_memory(request: MemoryParseRequest):
    parsed = parse_memory_with_gemini(request.memory)
    return MemoryParseResponse(memory=parsed)

@router.post("/memory/candidates", response_model=CandidateResponse)
def fetch_candidates(request: CandidateRequest):
    results = get_candidates(request.memory.model_dump(), request.additional_clues)
    
    # map to CandidateResult
    response_results = [
        CandidateResult(
            photo_id=r["photo_id"],
            score=r["score"],
            matched_clues=r["matched_clues"]
        )
        for r in results
    ]
    
    return CandidateResponse(
        candidate_count=len(response_results),
        results=response_results
    )

@router.post("/memory/candidates-details")
def fetch_candidates_details(request: CandidateRequest):
    # Same as above but includes photo_details for frontend rendering
    results = get_candidates(request.memory.model_dump(), request.additional_clues)
    return {
        "candidate_count": len(results),
        "results": results
    }

@router.post("/memory/next-clue", response_model=NextClueResponse)
def next_clue(request: NextClueRequest):
    # We need to simulate getting candidate clues
    results = get_candidates(request.memory.model_dump(), {})
    available_clues = extract_available_clues(results)
    
    clue_data = get_next_clue_with_gemini(request.memory.model_dump(), len(results), available_clues)
    
    return NextClueResponse(
        clue_dimension=clue_data.get("clue_dimension", "unknown"),
        question=clue_data.get("question", "Could you provide more context?"),
        options=clue_data.get("options", ["Not sure"])
    )

@router.post("/session/event")
def log_session_event(request: SessionEventRequest):
    # In a real app we would log to database or telemetry system
    print(f"TELEMETRY: {request.event} for session {request.session_id}")
    return {"status": "ok"}
