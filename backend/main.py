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
cors_origin = os.getenv("CORS_ORIGIN", "*")
origins = [o.strip() for o in cors_origin.split(",")] if cors_origin != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in origins else origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.endpoints import router as api_router
app.include_router(api_router, prefix="/api")

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
