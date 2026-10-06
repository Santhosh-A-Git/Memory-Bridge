import json
import os
from typing import List, Dict, Any

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "photos.json")

def load_photos() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def get_candidates(parsed_memory: dict, additional_clues: dict) -> List[Dict[str, Any]]:
    photos = load_photos()
    candidates = []
    
    # Extract known clues
    target_people = [p.lower() for p in parsed_memory.get("people", [])]
    target_events = [e.lower() for e in parsed_memory.get("events", [])]
    
    target_year = None
    time_clue = parsed_memory.get("time")
    if time_clue and time_clue.get("value"):
        try:
            target_year = int(time_clue.get("value")[:4])
        except ValueError:
            pass
            
    # Add any additional clues gathered from questions
    target_location = additional_clues.get("location", "").lower()
    
    for photo in photos:
        score = 0.0
        matched_clues = []
        
        # People match
        photo_people = [p.lower() for p in photo.get("people", [])]
        if target_people and any(p in photo_people for p in target_people):
            score += 0.3
            matched_clues.extend([p for p in target_people if p in photo_people])
            
        # Event match
        photo_events = [e.lower() for e in photo.get("event", [])]
        if target_events and any(e in photo_events for e in target_events):
            score += 0.3
            matched_clues.extend([e for e in target_events if e in photo_events])
            
        # Time match
        if target_year and photo.get("year") == target_year:
            score += 0.2
            matched_clues.append(str(target_year))
            
        # Additional Location match
        photo_location = (photo.get("location") or "").lower()
        if target_location and target_location != "not sure":
            if target_location == photo_location:
                score += 0.4
                matched_clues.append(photo.get("location"))
            elif target_location != "other":
                # Penalize if it explicitly does not match a known non-"other" location
                score -= 0.2
                
        if score > 0:
            candidates.append({
                "photo_id": photo["id"],
                "score": score,
                "matched_clues": list(set(matched_clues)),
                "photo_details": photo # include for UI rendering
            })
            
    # Sort by score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top N (e.g. 12)
    return candidates[:12]

def extract_available_clues(candidates: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    locations = set()
    years = set()
    for c in candidates:
        details = c["photo_details"]
        if details.get("location"):
            locations.add(details["location"])
        if details.get("year"):
            years.add(str(details["year"]))
            
    return {
        "locations": list(locations),
        "years": list(years)
    }
