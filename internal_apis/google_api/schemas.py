from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class STTRequest(BaseModel):
    file_url: HttpUrl
    headers: Optional[dict] = Field(None, description="The headers required to access the file (Ex: Bearer Token).")
    language_code: str = Field("hi-IN", description="Language code in BCP-47 format.")


class STTResponse(BaseModel):
    detected_text: list[dict]


class TranslateRequest(BaseModel):
    source_text: list[str]
    target_language: tuple[str, str] = Field(("en", "English"))


class TranslateResponse(BaseModel):
    detected_language: str
    translated_text: str
    translated_language: str


class ObjectDetectionRequest(BaseModel):
    file_url: str
    headers: dict


class ObjectDetectionResponse(BaseModel):
    detected_objects: list[list]
