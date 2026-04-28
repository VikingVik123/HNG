from fastapi import APIRouter, HTTPException, Depends, status, Query, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import csv
import io
from datetime import datetime
from db import get_db
from services.service import ProfileService
from utils import serialize_profile, serialize_profile_list
from auth.dependencies import get_current_user, require_admin
from models.user_model import Users
from exceptions import (
    APIException,
    InvalidRequestException,
    InvalidTypeException,
    ProfileNotFoundException,
    ExternalAPIException,
    ServerException,
)

router = APIRouter(prefix="/api", tags=["profiles"])

def build_pagination_links(page: int, limit: int, total: int, base_path: str, query_params: dict = None):
    """
    Build pagination links (self, next, prev) for paginated responses.
    """
    query_params = query_params or {}
    total_pages = (total + limit - 1) // limit  # Ceiling division
    
    # Build query string from params
    query_parts = []
    for key, value in query_params.items():
        if value is not None:
            query_parts.append(f"{key}={value}")
    
    base_query = "&".join(query_parts)
    separator = "&" if base_query else "?"
    
    # Self link
    self_link = f"{base_path}?page={page}&limit={limit}"
    if base_query:
        self_link = f"{base_path}?{base_query}&page={page}&limit={limit}"
    
    # Next link
    next_link = None
    if page < total_pages:
        next_link = f"{base_path}?{base_query}{separator}page={page + 1}&limit={limit}" if base_query else f"{base_path}?page={page + 1}&limit={limit}"
    
    # Prev link
    prev_link = None
    if page > 1:
        prev_link = f"{base_path}?{base_query}{separator}page={page - 1}&limit={limit}" if base_query else f"{base_path}?page={page - 1}&limit={limit}"
    
    return {
        "self": self_link,
        "next": next_link,
        "prev": prev_link
    }, total_pages

def get_api_version(x_api_version: str = Header(None)):
    """
    Validate that the X-API-Version header is present and set to '1'.
    """
    if not x_api_version:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "API version header required"}
        )
    if x_api_version != "1":
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "API version header required"}
        )
    return x_api_version

class CreateProfileRequest(BaseModel):
    name: str

@router.post("/profiles", status_code=status.HTTP_201_CREATED)
def create_profile(
    request: CreateProfileRequest,
    current_user: Users = Depends(get_current_user),
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
    api_version: str = Depends(get_api_version)
):
    """
    Create a new user profile by fetching data from external APIs and storing it in the database.
    Request body: {"name": "ella"}
    If a profile with the same name already exists, return it (idempotency).
    
    **Requires:** Admin role
    
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
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    api_version: str = Depends(get_api_version)
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
    
    # Build query params for links
    query_params = {}
    if gender:
        query_params["gender"] = gender
    if country_id:
        query_params["country_id"] = country_id
    if age_group:
        query_params["age_group"] = age_group
    if min_age:
        query_params["min_age"] = min_age
    if max_age:
        query_params["max_age"] = max_age
    if min_gender_probability:
        query_params["min_gender_probability"] = min_gender_probability
    if min_country_probability:
        query_params["min_country_probability"] = min_country_probability
    if sort_by:
        query_params["sort_by"] = sort_by
    if order != "asc":
        query_params["order"] = order
    
    links, total_pages = build_pagination_links(page, limit, result["total"], "/api/profiles", query_params)
    
    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": result["total"],
        "total_pages": total_pages,
        "links": links,
        "data": serialized_data
    }

@router.get("/profiles/search")
def search_profiles(
    q: str = Query(..., description="Natural language query"),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number (default: 1)"),
    limit: int = Query(10, ge=1, le=50, description="Results per page (default: 10, max: 50)"),
    api_version: str = Depends(get_api_version)
):
    """
    Search profiles using natural language query.
    
    **Requires:** Authentication
    
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
    
    # Build query params for links (include search query)
    query_params = {"q": q}
    
    links, total_pages = build_pagination_links(page, limit, result["total"], "/api/profiles/search", query_params)
    
    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": result["total"],
        "total_pages": total_pages,
        "links": links,
        "filters_used": result["filters_used"],
        "data": serialized_data
    }

@router.get("/profiles/export")
def export_profiles(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    gender: str = Query(None, description="Filter by gender (case-insensitive)"),
    country_id: str = Query(None, description="Filter by country ID (case-insensitive)"),
    age_group: str = Query(None, description="Filter by age group (case-insensitive)"),
    min_age: int = Query(None, description="Minimum age filter"),
    max_age: int = Query(None, description="Maximum age filter"),
    min_gender_probability: float = Query(None, description="Minimum gender probability (0-1)"),
    min_country_probability: float = Query(None, description="Minimum country probability (0-1)"),
    sort_by: str = Query(None, description="Sort by field: age | created_at | gender_probability"),
    order: str = Query("asc", description="Sort order: asc | desc"),
    format: str = Query("csv", description="Export format (currently supports: csv)"),
    api_version: str = Depends(get_api_version)
):
    """
    Export profiles as CSV file with all filters and sorting applied.
    Returns a downloadable CSV file with columns:
    id, name, gender, gender_probability, age, age_group, country_id, country_name, country_probability, created_at
    
    **Requires:** Authentication
    """
    if format.lower() != "csv":
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid export format. Supported formats: csv"}
        )
    
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
        page=1,
        limit=10000  # Large limit to get all filtered results
    )
    
    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        "id", "name", "gender", "gender_probability", "age", "age_group",
        "country_id", "country_name", "country_probability", "created_at"
    ])
    
    # Write data rows
    for profile in result["data"]:
        writer.writerow([
            profile.id,
            profile.name,
            profile.gender,
            profile.gender_probability,
            profile.age,
            profile.age_group,
            profile.country_id,
            profile.country_name,
            profile.country_probability,
            profile.created_at.isoformat() if hasattr(profile.created_at, 'isoformat') else str(profile.created_at)
        ])
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"profiles_{timestamp}.csv"
    
    # Prepare CSV content
    csv_content = output.getvalue().encode('utf-8')
    
    return FileResponse(
        io.BytesIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
    
@router.get("/profiles/{profile_id}")
def get_profile(
    profile_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    api_version: str = Depends(get_api_version)
):
    """
    Retrieve a user profile by its unique identifier.
    
    **Requires:** Authentication
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
def delete_profile(
    profile_id: str,
    current_user: Users = Depends(get_current_user),
    _: Users = Depends(require_admin),
    db: Session = Depends(get_db),
    api_version: str = Depends(get_api_version)
):
    """
    Delete a user profile by its unique identifier.
    Returns 204 No Content on success.
    
    **Requires:** Admin role
    """
    service = ProfileService(db)
    result = service.delete_profile(profile_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )
    return None
    