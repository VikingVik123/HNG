from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from service import ProfileService
from utils import serialize_profile, serialize_profile_list
from exceptions import (
    APIException,
    InvalidRequestException,
    InvalidTypeException,
    ProfileNotFoundException,
    ExternalAPIException,
    ServerException,
)

router = APIRouter(prefix="/api", tags=["profiles"])

class CreateProfileRequest(BaseModel):
    name: str

@router.post("/profiles", status_code=status.HTTP_201_CREATED)
def create_profile(request: CreateProfileRequest, db: Session = Depends(get_db)):
    """
    Create a new user profile by fetching data from external APIs and storing it in the database.
    Request body: {"name": "ella"}
    If a profile with the same name already exists, return it (idempotency).
    """
    # Validate input
    if not request.name or not isinstance(request.name, str):
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Missing or empty name"}
        )
    
    service = ProfileService(db)
    try:
        profile, is_existing = service.create_profile(request.name)
        serialized_profile = serialize_profile(profile)
        
        response = {"status": "success", "data": serialized_profile}
        if is_existing:
            response["message"] = "Profile already exists"
        return response
    except ExternalAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"status": "502", "message": e.message}
        )
    except APIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"status": "error", "message": e.message}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": "Internal server error"})
        
@router.get("/profiles")
def get_profiles(
    gender: str = Query(None),
    country_id: str = Query(None),
    age_group: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all user profiles with optional filtering.
    Query params: gender, country_id, age_group (case-insensitive)
    """
    service = ProfileService(db)
    profiles = service.get_profiles(gender=gender, country_id=country_id, age_group=age_group)
    serialized_data = [serialize_profile_list(p) for p in profiles]
    return {
        "status": "success",
        "count": len(profiles),
        "data": serialized_data
    }
    
@router.get("/profiles/{profile_id}")
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a user profile by its unique identifier.
    """
    service = ProfileService(db)
    profile = service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )
    serialized_profile = serialize_profile(profile)
    return {
        "status": "success",
        "data": serialized_profile
    }
    
@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """
    Delete a user profile by its unique identifier.
    Returns 204 No Content on success.
    """
    service = ProfileService(db)
    result = service.delete_profile(profile_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )
    return None
    service = ProfileService(db)
    try:
        success = service.delete_profile(profile_id)
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        return
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))