from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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
    
    **Duplicate Protection:**
    - Application-level idempotency check
    - Database UNIQUE constraint on 'name' column (final safety net)
    """
    # Validate input
    if not request.name or not isinstance(request.name, str):
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Missing or empty name", "code": "INVALID_NAME"}
        )
    
    service = ProfileService(db)
    try:
        profile, is_existing = service.create_profile(request.name)
        serialized_profile = serialize_profile(profile)
        
        response = {"status": "success", "data": serialized_profile}
        if is_existing:
            response["message"] = "Profile already exists (idempotent)"
        return response
        
    except IntegrityError as e:
        # Database UNIQUE constraint violation - final safety net for duplicates
        db.rollback()
        # Retrieve the existing profile
        try:
            profile = service.get_profile(request.name)
            if profile:
                serialized_profile = serialize_profile(profile)
                return {
                    "status": "success",
                    "data": serialized_profile,
                    "message": "Profile already exists (duplicate prevented by database constraint)"
                }
        except:
            pass
        raise HTTPException(
            status_code=409,
            detail={"status": "error", "message": "Duplicate profile", "code": "DUPLICATE_PROFILE"}
        )
        
    except ExternalAPIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"status": "502", "message": e.message, "code": "EXTERNAL_API_ERROR"}
        )
    except APIException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"status": "error", "message": e.message, "code": "INVALID_REQUEST"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": "Internal server error", "code": "INTERNAL_ERROR"}
        )
@router.get("/profiles")
def get_profiles(
    gender: str = Query(None, description="Filter by gender (case-insensitive)"),
    country_id: str = Query(None, description="Filter by country ID (case-insensitive)"),
    age_group: str = Query(None, description="Filter by age group (case-insensitive)"),
    min_age: int = Query(None, description="Minimum age filter"),
    max_age: int = Query(None, description="Maximum age filter"),
    min_gender_probability: float = Query(None, description="Minimum gender probability (0-1)"),
    min_country_probability: float = Query(None, description="Minimum country probability (0-1)"),
    sort_by: str = Query(None, description="Sort by field: age | created_at | gender_probability"),
    order: str = Query("asc", description="Sort order: asc | desc"),
    page: int = Query(1, ge=1, description="Page number (default: 1)"),
    limit: int = Query(10, ge=1, le=50, description="Results per page (default: 10, max: 50)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all user profiles with advanced optional filtering, sorting, and pagination.
    """
    service = ProfileService(db)
    result = service.get_profiles(
        gender=gender,
        country_id=country_id,
        age_group=age_group,
        min_age=min_age,
        max_age=max_age,
        min_gender_probability=min_gender_probability,
        min_country_probability=min_country_probability,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit
    )
    serialized_data = [serialize_profile_list(p) for p in result["data"]]
    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": result["total"],
        "data": serialized_data
    }

@router.get("/profiles/search")
def search_profiles(
    q: str = Query(..., description="Natural language query"),
    page: int = Query(1, ge=1, description="Page number (default: 1)"),
    limit: int = Query(10, ge=1, le=50, description="Results per page (default: 10, max: 50)"),
    db: Session = Depends(get_db)
):
    """
    Search profiles using natural language query.
    
    Query validation rules:
    - Must not be empty or whitespace-only
    - Must be between 2 and 200 characters
    - Must not contain only special characters
    """
    # Validate query parameter exists
    if not q:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid query parameters"}
        )
    
    q_stripped = q.strip()
    
    # Validate query is not empty after stripping
    if not q_stripped:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid query parameters"}
        )
    
    # Validate query length (minimum 2 characters, maximum 200)
    if len(q_stripped) < 2:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid query parameters"}
        )
    
    if len(q_stripped) > 200:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid query parameters"}
        )
    
    # Validate query contains at least some alphanumeric characters
    if not any(c.isalnum() for c in q_stripped):
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid query parameters"}
        )
    
    service = ProfileService(db)
    result = service.get_profiles_by_query(q_stripped, page=page, limit=limit)
    
    if result is None:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid query parameters"}
        )
    
    serialized_data = [serialize_profile_list(p) for p in result["data"]]
    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": result["total"],
        "filters_used": result["filters_used"],
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
    