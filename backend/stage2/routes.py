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
    gender: str = Query(None, description="Filter by gender (case-insensitive)"),
    country_id: str = Query(None, description="Filter by country ID (case-insensitive)"),
    age_group: str = Query(None, description="Filter by age group (case-insensitive)"),
    min_age: int = Query(None, description="Minimum age filter"),
    max_age: int = Query(None, description="Maximum age filter"),
    min_gender_probability: float = Query(None, description="Minimum gender probability (0-1)"),
    min_country_probability: float = Query(None, description="Minimum country probability (0-1)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all user profiles with advanced optional filtering.
    
    Supported filters:
    - gender: Filter by gender (case-insensitive)
    - age_group: Filter by age group (case-insensitive)
    - country_id: Filter by country ID (case-insensitive)
    - min_age: Minimum age (inclusive)
    - max_age: Maximum age (inclusive)
    - min_gender_probability: Minimum gender probability (0-1)
    - min_country_probability: Minimum country probability (0-1)
    
    Example: /api/profiles?gender=male&country_id=NG&min_age=25
    
    Filters are combinable and results strictly match all conditions.
    """
    service = ProfileService(db)
    profiles = service.get_profiles(
        gender=gender,
        country_id=country_id,
        age_group=age_group,
        min_age=min_age,
        max_age=max_age,
        min_gender_probability=min_gender_probability,
        min_country_probability=min_country_probability
    )
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
    