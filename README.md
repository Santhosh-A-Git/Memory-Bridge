# Memory Bridge

An AI-guided retrieval recovery experience for vague photo memories.

## Project Structure
- `/frontend`: Next.js frontend (React, Tailwind)
- `/backend`: FastAPI backend (Python)
- `/data`: Controlled demo library and mock data
- `/scripts`: Scripts to generate the mock dataset

## Requirements
- Node.js 18+
- Python 3.9+

## Local Setup

### 1. Environment Variables
Backend: Create a `.env` file in `/backend` with:
```
GEMINI_API_KEY=your_gemini_api_key_here
CORS_ORIGIN=http://localhost:3000
```

Frontend: Create a `.env.local` file in `/frontend` with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 2. Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Demo Data
The mock dataset is already generated at `/data/photos.json`. You can regenerate it by running `node scripts/generate_dataset.js` from the project root.

## Core MVP Architecture & Intelligence 🧠

This MVP was built to prove where intelligence is truly needed in the photo retrieval journey. It completely eliminates strict keyword requirements and acts as an intelligent conversational agent.

1. **Natural Language Parser (Invincible LLM Cascade)**
   Instead of forcing users to use metadata filters (e.g. `Date: 2022`), the user types a completely unstructured sentence (e.g., *"Find the photo of me with my friends at my goa trip"*).
   The backend uses an **Invincible LLM Cascade** (iterating through `gemini-3.1-pro-preview`, `gemini-2.5-flash`, `gemini-1.5-pro` until one perfectly succeeds, bypassing API limits or deprecations) to extract dimensions:
   - People: `["friends"]`
   - Events: `["goa trip"]`
   - Time: `None`
   
2. **Context-Aware Disambiguation (The "Memory Bridge")**
   The intelligence engine realizes that crucial dimensions (like Location or Exact Date) are missing. Instead of returning 100 random photos, it dynamically generates a contextual follow-up question: *"Do you remember the exact month or date of this trip?"*
   
3. **Targeted Retrieval (`search.py`)**
   Once the user provides the missing clue, the search algorithm maps the extracted entities to the exact structured metadata of the photos, scoring and filtering to return *only* the photos that precisely match the user's targeted memory.
