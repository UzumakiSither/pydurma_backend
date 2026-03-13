from datetime import datetime
from typing import Any, Optional, Annotated

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=3)


class UserLogin(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=3)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CollateRequest(BaseModel):
    texts: list[Annotated[str, Field(min_length=1)]] = Field(min_length=1)


class CollateCreateResponse(BaseModel):
    id: int
    status: str
    result: str


class CollationHistoryItem(BaseModel):
    id: int
    status: str
    created_at: datetime


class CollationDetailResponse(BaseModel):
    id: int
    status: str
    input_texts: Optional[list[str]] = None
    input_raw: Optional[str] = None
    result_text: Optional[str] = None
    weighted_matrix: Optional[Any] = None
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    created_at: datetime