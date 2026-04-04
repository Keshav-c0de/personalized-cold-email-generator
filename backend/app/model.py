import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
HTML_DIR = DATA_DIR / "html"
CAPTURES_FILE = DATA_DIR / "captures.jsonl"

_capture_write_lock = asyncio.Lock()


@dataclass(slots=True)
class CaptureRecord:
    id: int
    source_url: str
    page_title: str | None
    html_file_path: str
    html_preview: str
    created_at: datetime


async def save_capture_record(
    source_url: str,
    page_title: str | None,
    html_file_path: str,
) -> CaptureRecord:
    created_at = datetime.now(timezone.utc)
    html_preview = await _read_html_preview(html_file_path)

    async with _capture_write_lock:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        next_id = await _next_capture_id()

        record = CaptureRecord(
            id=next_id,
            source_url=source_url,
            page_title=page_title,
            html_file_path=html_file_path,
            html_preview=html_preview,
            created_at=created_at,
        )

        payload = {
            "id": record.id,
            "source_url": record.source_url,
            "page_title": record.page_title,
            "html_file_path": record.html_file_path,
            "html_preview": record.html_preview,
            "created_at": record.created_at.isoformat(),
        }
        await asyncio.to_thread(_append_jsonl, CAPTURES_FILE, payload)

    return record


async def _read_html_preview(html_file_path: str, max_len: int = 300) -> str:
    content = await asyncio.to_thread(Path(html_file_path).read_text, encoding="utf-8", errors="ignore")
    compact = " ".join(content.split())
    return compact[:max_len]


async def _next_capture_id() -> int:
    if not CAPTURES_FILE.exists():
        return 1

    lines = await asyncio.to_thread(CAPTURES_FILE.read_text, encoding="utf-8")
    entries = [line for line in lines.splitlines() if line.strip()]
    return len(entries) + 1


def _append_jsonl(path: Path, payload: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

