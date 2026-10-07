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
        
    model_name = os.getenv("GEMINI_TEXT_MODEL", "gemini-3.1-pro-preview")
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
    missing_clues: infer what important retrieval dimensions are MISSING (e.g., exact_date, location, people)
    - memory_confidence: high, medium, low
    
    You MUST respond with a raw JSON object containing these keys.
    
    Memory: "{memory_text}"
    """
    
    # We will use simple JSON mode parsing as the sdk supports it or simple regex
    try:
        response = model.generate_content(prompt)
        import json, re
        
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            raise ValueError("No JSON object could be extracted.")
            
        return ParsedMemory(**data)
    except Exception as e:
        error_msg = str(e).replace('"', "'")
        print(f"Gemini parsing failed: {error_msg}")
        return ParsedMemory(
            people=[],
            events=[f"ERROR: {error_msg}"[:200]],
            missing_clues=["api_failure"],
            memory_confidence="low"
        )

def get_next_clue_with_gemini(memory: dict, candidate_count: int, available_clues: dict) -> dict:
    if not api_key:
        return {
            "clue_dimension": "location",
            "question": "Do you remember which city this was in?",
            "options": ["Hyderabad", "Bengaluru", "Other", "Not sure"]
        }
        
    model_name = os.getenv("GEMINI_TEXT_MODEL", "gemini-3.1-pro-preview")
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
        response = model.generate_content(prompt)
        import json, re
        
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            raise ValueError("No JSON object could be extracted.")
    except Exception as e:
        print(f"Gemini next clue failed: {e}")
        missing = memory.get("missing_clues", ["location"])
        
        if "exact_date" in missing and "location" not in missing:
            return {
                "clue_dimension": "exact_date",
                "question": "Do you remember the exact month or date of this trip?",
                "options": ["Yes", "No, just the year", "Not sure"]
            }
        elif "people" in missing:
            return {
                "clue_dimension": "people",
                "question": "Who else was in the photo with you?",
                "options": ["Friends", "Family", "Colleagues", "Not sure"]
            }
        else:
            return {
                "clue_dimension": "location",
                "question": "Do you remember which city this was in?",
                "options": ["Hyderabad", "Bengaluru", "Mumbai", "Not sure"]
            }
