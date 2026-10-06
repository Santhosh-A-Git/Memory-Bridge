import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
import typing_extensions as typing
# pyrefly: ignore [missing-import]
from app.models.schemas import ParsedMemory

# Initialize Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def parse_memory_with_gemini(memory_text: str) -> ParsedMemory:
    if not api_key:
        # Fallback for testing when no key is set
        return ParsedMemory(
            people=["sister"],
            events=["college farewell"],
            time={"type": "approximate", "value": "2022"},
            missing_clues=["location", "exact_date"],
            memory_confidence="high"
        )
        
    model_name = os.getenv("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    You are an AI assistant helping to parse a user's vaguely remembered photo memory.
    Extract the following details if they exist in the memory text:
    - people (names or relationships)
    - places (cities, locations)
    - events (e.g., college farewell, birthday)
    - time (extract whether it's exact, approximate or relative, and the value)
    - objects
    - visual context
    - text visible in the photo
    - relationship_context
    - missing_clues: infer what important retrieval dimensions are MISSING (e.g., exact_date, location, people)
    - memory_confidence: high, medium, low
    
    Memory: "{memory_text}"
    """
    
    # We will use simple JSON mode parsing as the sdk supports it or simple regex
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                # To make this fully robust, we would pass the Pydantic schema
                # However, for MVP, we rely on the prompt to generate valid JSON matching the schema
            )
        )
        import json
        data = json.loads(response.text)
        return ParsedMemory(**data)
    except Exception as e:
        print(f"Gemini parsing failed: {e}")
        # Fallback
        return ParsedMemory(
            events=["unknown"],
            missing_clues=["exact_date", "location"],
            memory_confidence="low"
        )

def get_next_clue_with_gemini(memory: dict, candidate_count: int, available_clues: dict) -> dict:
    if not api_key:
        return {
            "clue_dimension": "location",
            "question": "Do you remember which city this was in?",
            "options": ["Hyderabad", "Bengaluru", "Other", "Not sure"]
        }
        
    model_name = os.getenv("GEMINI_TEXT_MODEL", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Based on the parsed memory and available candidates, decide the single best missing clue to ask for.
    You must only ask about a clue dimension that is currently MISSING.
    Do not ask more than 2 questions overall in a session (assume we're at step 1 or 2).
    
    Parsed Memory: {memory}
    Current candidate count: {candidate_count}
    Available candidate clues to disambiguate: {available_clues}
    
    Respond in JSON format with:
    {{
       "clue_dimension": "string",
       "question": "string",
       "options": ["option1", "option2", "Other", "Not sure"]
    }}
    Always include 'Not sure' in options.
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini next clue failed: {e}")
        return {
            "clue_dimension": "location",
            "question": "Could you provide a location?",
            "options": ["Yes", "No", "Not sure"]
        }
