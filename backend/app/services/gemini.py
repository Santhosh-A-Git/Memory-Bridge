import json
import os
import re
import traceback
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from app.models.schemas import ParsedMemory

# ── Initialize Gemini ──────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# ── KNOWN SYNONYM MAPS (to normalise LLM / NLP output → dataset values) ───────
EVENT_SYNONYMS = {
    "trip":             "vacation",
    "holiday":          "vacation",
    "goa trip":         "vacation",
    "tour":             "vacation",
    "outing":           "vacation",
    "farewell":         "college farewell",
    "graduation":       "college farewell",
    "convocation":      "college farewell",
    "party":            "birthday party",
    "bday":             "birthday party",
    "birthday":         "birthday party",
    "diwali celebration": "diwali",
    "new year party":   "new year",
    "new year eve":     "new year",
}

PLACE_SYNONYMS = {
    "hyd":          "Hyderabad",
    "hyderabad":    "Hyderabad",
    "bengaluru":    "Bengaluru",
    "bangalore":    "Bengaluru",
    "blr":          "Bengaluru",
    "mumbai":       "Mumbai",
    "bombay":       "Mumbai",
    "delhi":        "Delhi",
    "new delhi":    "Delhi",
    "goa":          "Goa",
    "chennai":      "Chennai",
    "pune":         "Pune",
}

def _canonicalise_event(raw: str) -> str:
    return EVENT_SYNONYMS.get(raw.lower().strip(), raw.strip())

def _canonicalise_place(raw: str) -> str:
    return PLACE_SYNONYMS.get(raw.lower().strip(), raw.strip())


# ── PRIMARY: parse with Gemini LLM ─────────────────────────────────────────────
def parse_memory_with_gemini(memory_text: str) -> ParsedMemory:
    if not api_key:
        # No API key — go straight to local NLP engine
        return _local_nlp_engine(memory_text)

    prompt = f"""
    You are an AI assistant helping to parse a user's vaguely remembered photo memory.
    Extract the following details if they exist in the memory text:
    - people (names or relationships, e.g. "sister", "friends", "dad")
    - places (cities or locations mentioned, e.g. "Hyderabad", "Goa")
    - events (e.g. "college farewell", "birthday party", "vacation")
    - time (extract whether it's exact, approximate or relative, and the value e.g. "2022", "3 years ago")
    - objects
    - visual context
    - text visible in the photo
    - relationship_context

    missing_clues: infer what important retrieval dimensions are MISSING from the memory.
    Possible missing clues: "location", "event", "people", "time"
    Only add a clue to missing_clues if it is genuinely absent from the user's text.

    Memory text: "{memory_text}"

    Respond ONLY with a valid JSON object, no markdown, no explanation:
    {{
        "people": [...],
        "places": [...],
        "events": [...],
        "time": {{"type": "approximate", "value": "..."}},
        "objects": [...],
        "visual": [...],
        "text": [...],
        "relationship_context": [...],
        "missing_clues": [...],
        "memory_confidence": "high"
    }}
    """

    models_to_try = [
        os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash"),
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
    ]

    errors = []
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt)

            # Extract JSON from response
            raw = response.text.strip()
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in response")

            data = json.loads(match.group(0))

            # Canonicalise events so they match dataset values
            raw_events = data.get("events") or []
            if isinstance(raw_events, str):
                raw_events = [raw_events]
            data["events"] = list({_canonicalise_event(e) for e in raw_events if e})

            # Canonicalise places
            raw_places = data.get("places") or []
            if isinstance(raw_places, str):
                raw_places = [raw_places]
            data["places"] = list({_canonicalise_place(p) for p in raw_places if p})

            # Recalculate missing_clues more reliably
            mc = []
            if not data.get("places"):        mc.append("location")
            if not data.get("events"):        mc.append("event")
            if not data.get("people"):        mc.append("people")
            time_val = (data.get("time") or {}).get("value") if isinstance(data.get("time"), dict) else data.get("time")
            if not time_val or time_val == "None": mc.append("time")
            data["missing_clues"] = mc

            return ParsedMemory(**data)

        except Exception as e:
            errors.append(f"{m_name}: {str(e)}")

    # All Gemini models failed
    print(f"[gemini.py] All Gemini models failed: {errors}")
    return _local_nlp_engine(memory_text)


# ── FALLBACK: Local NLP Engine ─────────────────────────────────────────────────
def _local_nlp_engine(memory_text: str) -> ParsedMemory:
    """
    Zero-API keyword scanner that works entirely from the dataset + synonym maps.
    Guaranteed never to throw an exception — returns a safe ParsedMemory object.
    """
    try:
        lower = memory_text.lower()
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "photos.json")

        all_people: set = set()
        all_events: set = set()
        all_locs: set = set()

        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                photos = json.load(f)
            for p in photos:
                all_people.update(p.get("people", []))
                all_events.update(p.get("event", []))
                loc = p.get("location")
                if loc:
                    all_locs.add(loc)   # keep original casing

        # Expand synonyms for matching
        synonym_events = set(EVENT_SYNONYMS.keys())
        all_events_expanded = all_events | synonym_events

        synonym_places = set(PLACE_SYNONYMS.keys())
        all_locs_expanded = all_locs | {k for k in synonym_places}

        # --- Match people ---
        found_people = [p for p in all_people if p.lower() in lower]

        # --- Match events ---
        raw_found_events = []
        for e in all_events_expanded:
            if e.lower() in lower:
                raw_found_events.append(e)
        found_events = list({_canonicalise_event(e) for e in raw_found_events})

        # --- Match locations ---
        found_cities = []
        for loc in all_locs_expanded:
            if loc.lower() in lower:
                found_cities.append(_canonicalise_place(loc))
        found_cities = list(set(found_cities))

        # --- Match year ---
        found_year = None
        year_match = re.search(r"(20[0-9]{2})", lower)
        if year_match:
            found_year = year_match.group(1)

        # Handle relative time like "3 years ago"
        if not found_year:
            rel_match = re.search(r"(\d+)\s+years?\s+ago", lower)
            if rel_match:
                approx_year = 2024 - int(rel_match.group(1))
                found_year = str(approx_year)

        # --- Compute missing clues ---
        missing_clues = []
        if not found_cities:    missing_clues.append("location")
        if not found_events:    missing_clues.append("event")
        if not found_people:    missing_clues.append("people")
        if not found_year:      missing_clues.append("time")

        return ParsedMemory(
            people=found_people,
            places=found_cities,
            events=found_events,
            time={"type": "approximate", "value": found_year},
            missing_clues=missing_clues,
            memory_confidence="high",
        )

    except Exception:
        err = traceback.format_exc()
        print(f"[gemini.py] Local NLP engine crashed:\n{err}")
        # Absolute last resort — return empty parsed memory so UI still works
        return ParsedMemory(missing_clues=["location", "event", "people", "time"], memory_confidence="low")


# ── Clue question generator ────────────────────────────────────────────────────
def get_next_clue_with_gemini(memory: dict, candidate_count: int, available_clues: dict) -> dict:
    """
    Decide the single best follow-up question based on the FIRST missing clue.
    Tries Gemini first; falls back to deterministic rule-based logic.
    """
    missing = memory.get("missing_clues") or []

    if api_key:
        prompt = f"""
        Based on the parsed memory below, decide the single best follow-up question to narrow down the photo.
        Ask about the FIRST item in missing_clues only.
        Use the available_clues to build specific, helpful options (not generic ones).

        Parsed Memory: {json.dumps(memory)}
        Available clue options from candidates: {json.dumps(available_clues)}
        Missing clues: {missing}

        Respond ONLY with a valid JSON object:
        {{
            "clue_dimension": "location|event|people|time",
            "question": "...",
            "options": ["option1", "option2", "option3", "Not sure"]
        }}
        Always include 'Not sure' as the last option.
        """

        models_to_try = [
            os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash"),
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-pro",
        ]

        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content(prompt)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    if isinstance(data, dict) and "clue_dimension" in data:
                        # Ensure 'Not sure' is always present
                        opts = data.get("options", [])
                        if "Not sure" not in opts:
                            opts.append("Not sure")
                        data["options"] = opts
                        return data
            except Exception as e:
                print(f"[gemini.py] next-clue model {m_name} failed: {e}")
                continue

    # ── Deterministic fallback ─────────────────────────────────────────────────
    return _deterministic_next_clue(missing, available_clues)


def _deterministic_next_clue(missing: list, available_clues: dict) -> dict:
    """Always returns a well-formed clue question from deterministic rules."""

    if "event" in missing:
        opts = available_clues.get("events") or []
        # Humanise canonical event labels
        label_map = {
            "college farewell": "College Farewell",
            "birthday party":   "Birthday Party",
            "vacation":         "Vacation / Trip",
            "wedding":          "Wedding",
            "diwali":           "Diwali",
            "new year":         "New Year",
        }
        display_opts = [label_map.get(o, o.title()) for o in opts] if opts else ["Birthday", "Vacation", "Wedding", "College Farewell"]
        if "Not sure" not in display_opts:
            display_opts.append("Not sure")
        return {
            "clue_dimension": "event",
            "question": "What kind of occasion or event was this?",
            "options": display_opts[:5],
        }

    if "people" in missing:
        opts = available_clues.get("people") or []
        display_opts = [o.title() for o in opts] if opts else ["Friends", "Family", "Colleagues"]
        if "Not sure" not in display_opts:
            display_opts.append("Not sure")
        return {
            "clue_dimension": "people",
            "question": "Who else was in the photo with you?",
            "options": display_opts[:5],
        }

    if "location" in missing:
        opts = available_clues.get("locations") or []
        display_opts = opts if opts else ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Other"]
        if "Not sure" not in display_opts:
            display_opts.append("Not sure")
        return {
            "clue_dimension": "location",
            "question": "Do you remember which city this was in?",
            "options": display_opts[:6],
        }

    if "time" in missing:
        opts = available_clues.get("years") or []
        display_opts = opts if opts else ["2019", "2020", "2021", "2022", "2023"]
        if "Not sure" not in display_opts:
            display_opts.append("Not sure")
        return {
            "clue_dimension": "time",
            "question": "Do you remember which year this was taken?",
            "options": display_opts[:6],
        }

    # Nothing is missing — should not reach here normally
    return {
        "clue_dimension": "location",
        "question": "Do you remember which city this was in?",
        "options": ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Other", "Not sure"],
    }
