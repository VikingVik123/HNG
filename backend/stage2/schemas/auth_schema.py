from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class GitHubAuthRequest(BaseModel):
    pass

class TokenResponse(BaseModel):
    pass
class RefreshTokenRequest(BaseModel):
    pass
class RefreshTokenResponse(BaseModel):
    pass

    