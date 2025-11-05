from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from app.database.db import Base


class StringRecord(Base):
    __tablename__ = "strings"
    id          = Column(String, primary_key=True)
    value       = Column(String, nullable=False, unique=True)
    length      = Column(Integer)
    is_palindrome = Column(Boolean)
    unique_characters = Column(Integer)
    word_count  = Column(Integer)
    sha256_hash = Column(String)
    character_frequency_map = Column(JSON)
    created_at  = Column(DateTime)