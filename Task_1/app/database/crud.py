from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.string import StringRecord


class StringCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_string_by_id(self, string_id: str):
        return self.db.query(StringRecord).filter(StringRecord.id == string_id).first()

    def create_string(self, string_record: StringRecord):
        self.db.add(string_record)
        self.db.commit()
        self.db.refresh(string_record)
        return string_record
