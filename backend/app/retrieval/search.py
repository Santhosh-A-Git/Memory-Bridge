import json
import os
from typing import List, Dict, Any
import traceback

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "photos.json")

def load_photos() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def get_candidates(parsed_memory: dict, additional_clues: dict) -> List[Dict[str, Any]]:
    try:
        photos = load_photos()
        candidates = []
        
        # Safely extract known clues ensuring they are lists and not None
        raw_people = parsed_memory.get("people") or []
        if isinstance(raw_people, str): raw_people = [raw_people]
        target_people = [str(p).lower() for p in raw_people]
        
        raw_events = parsed_memory.get("events") or []
        if isinstance(raw_events, str): raw_events = [raw_events]
        target_events = [str(e).lower() for e in raw_events]
        
        target_year = None
        time_clue = parsed_memory.get("time")
        if time_clue:
            time_str = str(time_clue.get("value")) if isinstance(time_clue, dict) else str(time_clue)
            import re
            year_match = re.search(r'(20[0-9]{2})', time_str)
            if year_match:
                target_year = int(year_match.group(1))
                
        # Add any additional clues gathered from questions
        target_location = additional_clues.get("location", "").lower()
        
        # If the LLM already extracted places, combine them
        places = parsed_memory.get("places")
        if places:
            target_location = str(places[0]).lower() if isinstance(places, list) and len(places) > 0 else str(places).lower()
        
        for photo in photos:
            score = 0.0
            matched_clues = []
            
            # People match
            photo_people = [p.lower() for p in photo.get("people", [])]
            if target_people:
                for tp in target_people:
                    for pp in photo_people:
                        if tp in pp or pp in tp:
                            score += 0.3
                            matched_clues.append(pp)
                            break
                
            # Event match
            photo_events = [e.lower() for e in photo.get("event", [])]
            if target_events:
                for te in target_events:
                    for pe in photo_events:
                        if te in pe or pe in te:
                            score += 0.3
                            matched_clues.append(pe)
                            break
                
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
                    score -= 0.2
                    
            if score > 0:
                candidates.append({
                    "photo_id": photo["id"],
                    "score": score,
                    # Ensure no None types end up in matched_clues
                    "matched_clues": list(set([str(c) for c in matched_clues if c is not None])),
                    "photo_details": photo # include for UI rendering
                })
                
        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top N (e.g. 12)
        return candidates[:12]
    except Exception as e:
        err_msg = str(e) + " | " + traceback.format_exc()
        return [{
            "photo_id": "ERROR_PHOTO",
            "score": 99.9,
            "matched_clues": ["ERROR", err_msg[:100]],
            "photo_details": {
                "id": "ERROR",
                "image_url": "https://placehold.co/600x400?text=CRASH+" + err_msg.replace(" ", "+").replace("\n", "")[:50],
                "year": 2024,
                "location": "Error City"
            }
        }]

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
