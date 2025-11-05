from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.database.db import get_session
from app.models.country import Country

router = APIRouter(tags=["Status"])

@router.get("/status")
def get_status(session: Session = Depends(get_session)):
    total = session.exec(select(func.count(Country.id))).one()
    last_refreshed = session.exec(select(func.max(Country.last_refreshed_at))).one()
    return {
        "total_countries": total,
        "last_refreshed_at": last_refreshed
    }
