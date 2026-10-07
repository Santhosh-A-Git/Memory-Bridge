# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class TimeClue(BaseModel):
    type: str = Field(description="exact, approximate, or relative")
    value: Optional[str] = None

class ParsedMemory(BaseModel):
    people: Optional[List[str]] = None
    places: Optional[List[str]] = None
    events: Optional[List[str]] = None
    time: Optional[TimeClue] = None
    objects: Optional[List[str]] = None
    visual: Optional[List[str]] = None
    text: Optional[List[str]] = None
    relationship_context: Optional[List[str]] = None
    missing_clues: Optional[List[str]] = None
    memory_confidence: str = Field(default="unknown")

class MemoryParseRequest(BaseModel):
    memory: str

class MemoryParseResponse(BaseModel):
    memory: ParsedMemory

class CandidateRequest(BaseModel):
    memory: ParsedMemory
    additional_clues: Dict[str, Any] = {}

class CandidateResult(BaseModel):
    photo_id: str
    score: float
    matched_clues: List[str]

class CandidateResponse(BaseModel):
    candidate_count: int
    results: List[CandidateResult]

class NextClueRequest(BaseModel):
    memory: ParsedMemory
    candidate_ids: List[str]

class NextClueResponse(BaseModel):
    clue_dimension: str
    question: str
    options: List[str]

class SessionEventRequest(BaseModel):
    session_id: str
    event: str
    metadata: Dict[str, Any] = {}
