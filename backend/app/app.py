import asyncio
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.agent import generate_email
from app.beatify import extract_info

from app.model import DATA_DIR, HTML_DIR, save_capture_record
from app.schema import CaptureResponse, PageCapture

APP_DIR = Path(__file__).resolve().parent
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app = FastAPI(title="HTML Capture API", version="0.1.0")

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^chrome-extension://[a-p]{32}$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _is_local_environment() -> bool:
    return os.getenv("CAPTURE_API_LOCAL_ONLY", "true").lower() not in {"0", "false", "no"}


@app.on_event("startup")
async def startup_event() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "local_only": str(_is_local_environment()).lower()}


@app.post("/capture", response_model=CaptureResponse)
async def capture_page(payload: PageCapture) -> CaptureResponse:
    if _is_local_environment() and payload.source_url.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http and https source URLs are allowed.")

    if not payload.html.strip():
        raise HTTPException(status_code=400, detail="HTML content cannot be empty.")

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    file_name = f"capture-{timestamp}-{uuid4().hex}.html"
    file_path = HTML_DIR / file_name
    await asyncio.to_thread(file_path.write_text, payload.html, encoding="utf-8")
    extracted_info = await asyncio.to_thread(extract_info, payload.html)

    email_response: str | None = None
    if payload.prompt:
        email_response = await generate_email(payload.prompt, extracted_info)

    record = await save_capture_record(
        source_url=str(payload.source_url),
        page_title=payload.page_title,
        html_file_path=str(file_path),
    )

    return CaptureResponse(
        id=record.id,
        source_url=record.source_url,
        page_title=record.page_title,
        html_file_path=record.html_file_path,
        created_at=record.created_at,
        email_response=email_response,
    )
    
