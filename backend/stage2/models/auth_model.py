from sqlalchemy import Column, Integer, String, DateTime, UUID, Float, Index, Boolean
from db import Base
from uuid6 import uuid7
from datetime import datetime, timezone


class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    is_revoked = Column(Boolean, nullable=False, default=False)