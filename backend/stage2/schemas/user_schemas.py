from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LoginResponse(BaseModel):
    message: str
    access_token: str