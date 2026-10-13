import json
import os
import re
import traceback
from typing import List, Dict, Any

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

        # ── 1. Extract people ──────────────────────────────────────────────────
        raw_people = parsed_memory.get("people") or []
        if isinstance(raw_people, str):
            raw_people = [raw_people]
        target_people = [str(p).lower() for p in raw_people if p]

        # Merge people from additional_clues
        ac_people = additional_clues.get("people", "")
        if ac_people and ac_people.lower() not in ("not sure", "skip", ""):
            target_people.append(ac_people.lower())

        # ── 2. Extract events ──────────────────────────────────────────────────
        raw_events = parsed_memory.get("events") or []
        if isinstance(raw_events, str):
            raw_events = [raw_events]
        target_events = [str(e).lower() for e in raw_events if e]

        # Merge events from additional_clues
        ac_event = additional_clues.get("event", "")
        if ac_event and ac_event.lower() not in ("not sure", "skip", ""):
            # Map user-friendly option labels to canonical dataset values
            event_map = {
                "birthday": "birthday party",
                "birthday party": "birthday party",
                "vacation": "vacation",
                "trip": "vacation",
                "holiday": "vacation",
                "wedding": "wedding",
                "farewell": "college farewell",
                "college farewell": "college farewell",
                "graduation": "college farewell",
                "diwali": "diwali",
                "new year": "new year",
            }
            mapped = event_map.get(ac_event.lower(), ac_event.lower())
            target_events.append(mapped)

        # ── 3. Extract year ────────────────────────────────────────────────────
        target_year = None
        time_clue = parsed_memory.get("time")
        if time_clue:
            time_str = str(time_clue.get("value")) if isinstance(time_clue, dict) else str(time_clue)
            if time_str and time_str != "None":
                year_match = re.search(r"(20[0-9]{2})", time_str)
                if year_match:
                    target_year = int(year_match.group(1))

        # Also handle relative time like "3 years ago"
        ac_time = additional_clues.get("time", "")
        if not target_year and ac_time and ac_time.lower() not in ("not sure", ""):
            year_match = re.search(r"(20[0-9]{2})", ac_time)
            if year_match:
                target_year = int(year_match.group(1))

        # ── 4. Extract location ────────────────────────────────────────────────
        # Priority: additional_clues > parsed_memory.places
        ac_location = additional_clues.get("location", "").lower().strip()

        places = parsed_memory.get("places") or []
        if isinstance(places, str):
            places = [places]
        parsed_location = str(places[0]).lower().strip() if places else ""

        # Use whichever we have; additional_clues (user answer) takes priority
        target_location = ac_location if ac_location else parsed_location

        # ── 5. Score photos ────────────────────────────────────────────────────
        for photo in photos:
            score = 0.0
            matched_clues = []

            # People match (substring both ways)
            photo_people = [str(p).lower() for p in photo.get("people", [])]
            if target_people:
                for tp in target_people:
                    for pp in photo_people:
                        if tp in pp or pp in tp:
                            score += 0.35
                            matched_clues.append(pp)
                            break

            # Event match (substring both ways)
            photo_events = [str(e).lower() for e in photo.get("event", [])]
            if target_events:
                for te in target_events:
                    for pe in photo_events:
                        if te in pe or pe in te:
                            score += 0.35
                            matched_clues.append(pe)
                            break

            # Year match
            if target_year and photo.get("year") == target_year:
                score += 0.2
                matched_clues.append(str(target_year))

            # Location match — case-insensitive exact match after lowering both sides
            photo_location = (photo.get("location") or "").lower().strip()
            if target_location and target_location not in ("not sure", "other", "skip", ""):
                if target_location == photo_location:
                    score += 0.4
                    matched_clues.append(photo.get("location", ""))
                elif target_location not in ("other",):
                    # Mild penalty for wrong city when user was specific
                    score -= 0.15

            if score > 0:
                candidates.append({
                    "photo_id": photo["id"],
                    "score": score,
                    "matched_clues": list({str(c) for c in matched_clues if c}),
                    "photo_details": photo,
                })

        # Sort by score descending and return top 12
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:12]

    except Exception:
        err = traceback.format_exc()
        print(f"[search.py] get_candidates crashed:\n{err}")
        return []   # Return empty list — frontend handles gracefully via fallback screen


def extract_available_clues(candidates: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    locations: set = set()
    years: set = set()
    events: set = set()
    people: set = set()

    for c in candidates:
        details = c.get("photo_details", {})
        loc = details.get("location")
        if loc:
            locations.add(loc)
        yr = details.get("year")
        if yr:
            years.add(str(yr))
        for ev in details.get("event", []):
            if ev:
                events.add(ev)
        for p in details.get("people", []):
            if p:
                people.add(p)

    return {
        "locations": sorted(locations),
        "years": sorted(years),
        "events": sorted(events),
        "people": sorted(people),
    }
