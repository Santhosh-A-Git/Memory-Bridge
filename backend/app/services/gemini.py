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
    
    models_to_try = [
        os.getenv("GEMINI_TEXT_MODEL", "gemini-3.1-pro-preview"),
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash"
    ]
    
    errors = []
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt)
            import json, re
            
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return ParsedMemory(**data)
            else:
                raise ValueError(f"No JSON object found in {m_name}")
        except Exception as e:
            errors.append(f"{m_name}: {str(e)}")
            continue
            
    # If all models fail due to Quota/429
    error_msg = str(errors[0]).replace('"', "'") if errors else "Unknown API Failure"
    print(f"Gemini parsing failed. Falling back to Local NLP Engine due to: {error_msg}")
    
    # ---------------------------------------------------------
    # LOCAL NLP ENGINE (Zero-API Fallback for MVP Dataset)
    # ---------------------------------------------------------
    lower_text = memory_text.lower()
    
    import json, os, re
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "photos.json")
    
    found_people, found_events, found_cities = [], [], []
    found_year = None
    
    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            photos = json.load(f)
            
        all_people = set(p.lower() for photo in photos for p in photo.get("people", []))
        all_events = set(e.lower() for photo in photos for e in photo.get("event", []))
        all_locs = set((photo.get("location") or "").lower() for photo in photos if photo.get("location"))
        
        # Add common synonyms
        if "vacation" in all_events: all_events.update(["trip", "goa", "holiday"])
        if "college farewell" in all_events: all_events.update(["farewell", "graduation"])
        
        for p in all_people:
            if p in lower_text: found_people.append(p)
            
        raw_found_events = []
        for e in all_events:
            if e in lower_text: raw_found_events.append(e)
            
        for l in all_locs:
            if l in lower_text: found_cities.append(l)
            
        # Map synonyms back to canonical dataset events so search.py works!
        for e in raw_found_events:
            if e in ["trip", "goa", "holiday"]:
                found_events.append("vacation")
            elif e in ["farewell", "graduation"]:
                found_events.append("college farewell")
            else:
                found_events.append(e)
        found_events = list(set(found_events))
            
    year_match = re.search(r'(20[0-9]{2})', lower_text)
    if year_match: found_year = year_match.group(1)
        
    missing_clues = []
    if not found_cities: missing_clues.append("location")
    if found_year and not re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', lower_text):
        missing_clues.append("exact_date")
    if not found_people and not found_events and not found_year and not found_cities:
        missing_clues.append("event") # if completely vague
        
    return ParsedMemory(
        people=found_people,
        events=found_events,
        time={"type": "approximate", "value": found_year},
        missing_clues=missing_clues,
        memory_confidence="high"
    )

def get_next_clue_with_gemini(memory: dict, candidate_count: int, available_clues: dict) -> dict:
    if not api_key:
        return {
            "clue_dimension": "location",
            "question": "Do you remember which city this was in?",
            "options": ["Hyderabad", "Bengaluru", "Other", "Not sure"]
        }
        
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
    
    models_to_try = [
        os.getenv("GEMINI_TEXT_MODEL", "gemini-3.1-pro-preview"),
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    last_error = None
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt)
            import json, re
            
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                raise ValueError("No JSON object could be extracted.")
        except Exception as e:
            last_error = e
            continue
            
    print(f"Gemini next clue failed on all models: {last_error}")
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
