from datetime import datetime
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator

class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("A valid email address is required")
        return normalized

class LoginRequest(BaseModel):
    # Login must accept the credentials of existing accounts. Password-strength
    # requirements belong to registration, not authentication.
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("A valid email address is required")
        return normalized

class AdminLoginRequest(BaseModel):
    access_key: str = Field(min_length=1, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ComplaintCreate(BaseModel):
    description: str = Field(min_length=10, max_length=5000)
    title: str | None = Field(default=None, max_length=180)
    location: str | None = Field(default=None, max_length=255)
    locality: str | None = Field(default=None, max_length=120)
    landmark: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    preferred_language: str | None = Field(default=None, max_length=40)
    category: str | None = Field(default=None, max_length=80)
    supporting_information: str | None = Field(default=None, max_length=5000)

class ComplaintUpdate(BaseModel):
    status: str | None = None
    category: str | None = None
    urgency: str | None = None
    department: str | None = Field(default=None, max_length=100)
    admin_note: str | None = Field(default=None, max_length=5000)
    priority: str | None = Field(default=None, max_length=20)

class PredictionOut(BaseModel):
    field: str
    value: str
    confidence: str | None
    method: str
    human_correction: str | None
    model_config = ConfigDict(from_attributes=True)

class ComplaintOut(BaseModel):
    id: int
    reference: str | None = None
    title: str | None = None
    description: str
    location: str | None
    locality: str | None = None
    landmark: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    preferred_language: str | None = None
    detected_language: str | None = None
    intent: str | None = None
    category: str | None
    urgency: str | None
    sentiment: str | None
    status: str
    department: str | None
    priority: str | None = None
    admin_note: str | None
    created_at: datetime
    predictions: list[PredictionOut] = []
    model_config = ConfigDict(from_attributes=True)

class ResponseCreate(BaseModel):
    message: str = Field(min_length=1, max_length=5000)

class TranslationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    source_language: str = Field(min_length=2, max_length=32)
    target_language: str = Field(min_length=2, max_length=32)

class SummaryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    output_language: str = Field(default="original", max_length=32)
    detail: str = Field(default="short", pattern="^(short|detailed)$")
