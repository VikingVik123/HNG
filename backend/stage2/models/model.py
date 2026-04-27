from sqlalchemy import Column, Integer, String, DateTime, UUID, Float, Index, Boolean
from db import Base
from uuid6 import uuid7
from datetime import datetime, timezone

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    # UNIQUE CONSTRAINT: name must be unique across all profiles
    # This prevents duplicate records at the database level
    name = Column(String, nullable=False, unique=True, index=True)
    gender = Column(String, nullable=True)
    gender_probability = Column(Float, nullable=True)
    sample_size = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    age_group = Column(String, nullable=True)
    country_id = Column(String, nullable=True)
    country_name = Column(String, nullable=True)
    country_probability = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Create unique index on name for enforcement and performance
    __table_args__ = (
        Index('ix_profile_name_unique', 'name', unique=True),
    )



