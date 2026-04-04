from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class PageCapture(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    source_url: HttpUrl = Field(..., examples=["https://example.com"])
    page_title: str | None = Field(default=None, max_length=512, examples=["Example"])
    html: str = Field(..., min_length=1, max_length=5_000_000)
    prompt: str | None = Field(default=None, max_length=2_000)


class CaptureResponse(BaseModel):
    id: int
    source_url: str
    page_title: str | None
    html_file_path: str
    created_at: datetime
    email_response: str | None = None