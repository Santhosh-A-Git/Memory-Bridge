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

## Architecture
- The frontend captures natural language memory and communicates with the backend APIs.
- The backend parses the memory using Gemini API, identifying the missing clues.
- The retrieval module deterministically finds candidates based on known clues.
- The next-clue reasoner identifies the highest-value missing detail and generates a question.
- Once answered, candidates are re-ranked, and the refined list is sent to the UI for visual recognition.
