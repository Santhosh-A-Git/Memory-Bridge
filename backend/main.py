# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Memory Bridge API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.endpoints import router as api_router
app.include_router(api_router, prefix="/api")

@app.get("/healthz")
def health_check():
    import traceback
    try:
        from app.services.gemini import parse_memory_with_gemini
        result = parse_memory_with_gemini("test memory")
        return {"status": "ok", "result": result.model_dump()}
    except Exception as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
