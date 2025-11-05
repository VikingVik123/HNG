from pydantic import BaseModel, Field
from datetime import datetime


class StringIn(BaseModel):
    value: str = Field(..., min_length=1)
class StringOut(BaseModel):
    id: str
    value: str
    properties: dict
    created_at: datetime
    class Config:
        orm_mode = True