from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProfileResponse(BaseModel):
    id: str
    name: str
    gender: Optional[str] = None
    gender_probability: Optional[float] = None
    sample_size: Optional[float] = None
    age: Optional[int] = None
    age_group: Optional[str] = None
    country_id: Optional[str] = None
    country_name: Optional[str] = None
    country_probability: Optional[float] = None
    created_at: str

    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    age_group: Optional[str] = None
    country_id: Optional[str] = None
    country_name: Optional[str] = None

    class Config:
        from_attributes = True
