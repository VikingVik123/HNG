from sqlalchemy import Column, Integer, String, DateTime, UUID, Float, Index, Boolean
from db import Base
from uuid6 import uuid7
from datetime import datetime, timezone


class Users(Base):
        __tablename__ = "users"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
        github_id = Column(String, nullable=False, unique=True, index=True)
        username = Column(String, nullable=False, unique=True, index=True)
        email = Column(String, nullable=True, unique=True, index=True)
        avatar_url = Column(String, nullable=True)
        role = Column(String, nullable=False, default="analyst")
        is_active = Column(Boolean, nullable=False, default=True)
        last_login_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
        created_at = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))
