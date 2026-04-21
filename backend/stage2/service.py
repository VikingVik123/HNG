import httpx
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from db import get_db
from model import Profile
from exceptions import ExternalAPIException, ProfileNotFoundException

load_dotenv()

genderize_url = os.getenv("Genderize")
agify_url = os.getenv("Agify")
nationalize_url = os.getenv("Nationalize")

class ProfileService:
    """
    Service to manage user profiles and their interactions with the HNG internship program.
    This service provides functionalities to create, retrieve, update, and delete user profiles
    """
    def __init__(self, db):
        self.db = db

    def create_profile(self, name: str):
        """
        Create a new user profile by fetching data from external APIs and storing it in the database.
        If a profile with the same name already exists, return it (idempotency).
        Returns: (profile, is_existing) tuple
        """
        # Check if profile already exists (idempotency)
        existing_profile = self.db.query(Profile).filter(Profile.name == name).first()
        if existing_profile:
            return (existing_profile, True)  # Return existing profile with flag
        
        # Fetch data from external APIs
        # gender data from Genderize API
        gender_data = httpx.get(f"{genderize_url}{name}").json()
        gender = gender_data.get("gender")
        gender_probability = gender_data.get("probability")
        sample_size = gender_data.get("count")
        
        # Edge case: Genderize returns gender: null or count: 0
        if gender is None or sample_size == 0:
            raise ExternalAPIException("Genderize")

        # age data from Agify
        age_data = httpx.get(f"{agify_url}{name}").json()
        age = age_data.get("age")
        
        # Edge case: Agify returns age: null
        if age is None:
            raise ExternalAPIException("Agify")
        
        age_group = None
        if age <= 12:
            age_group = "child"
        elif 13 <= age <= 19:
            age_group = "teenager"
        elif 20 <= age <= 59:
            age_group = "adult"
        else:
            age_group = "senior"

        # country data from Nationalize
        country_data = httpx.get(f"{nationalize_url}{name}").json()
        countries = country_data.get("country", [])
        country_id = None
        country_name = None

        country_probability = None

        # Edge case: Nationalize returns no country data
        if not countries:
            raise ExternalAPIException("Nationalize")
        
        # Find the country with the highest probability
        highest_country = max(countries, key=lambda x: x.get("probability", 0))
        country_id = highest_country.get("country_id")
        country_probability = highest_country.get("probability")
        # Create a new profile instance
        profile = Profile(
            name=name,
            gender=gender,
            gender_probability=gender_probability,
            sample_size=sample_size,
            age=age,
            age_group=age_group,
            country_id=country_id,
            country_name=country_name,
            country_probability=country_probability,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(profile)
        self.db.commit()
        return (profile, False)  # Return new profile with flag

    def get_profile(self, profile_id: str):
        """
        Retrieve a user profile by its unique identifier.
        """
        try:
            profile_uuid = UUID(profile_id)
            return self.db.query(Profile).filter(Profile.id == profile_uuid).first()
        except (ValueError, TypeError):
            return None
    
    def get_profiles(
        self,
        gender: str = None,
        country_id: str = None,
        age_group: str = None,
        min_age: int = None,
        max_age: int = None,
        min_gender_probability: float = None,
        min_country_probability: float = None,
        sort_by: str = None,
        order: str = "asc",
        skip: int = 0,
        limit: int = 100
    ):
        """
        Retrieve a list of user profiles with advanced optional filtering and sorting.
        
        Supports filtering by:
        - gender (case-insensitive partial match)
        - country_id (case-insensitive partial match)
        - age_group (case-insensitive partial match)
        - min_age (minimum age)
        - max_age (maximum age)
        - min_gender_probability (minimum gender probability)
        - min_country_probability (minimum country probability)
        
        Supports sorting by:
        - age: Sort by age
        - created_at: Sort by creation date
        - gender_probability: Sort by gender probability
        
        All filters are combinable and results strictly match all conditions.
        """
        query = self.db.query(Profile)
        
        # Apply categorical filters (case-insensitive)
        if gender:
            query = query.filter(Profile.gender.ilike(f"%{gender}%"))
        if country_id:
            query = query.filter(Profile.country_id.ilike(f"%{country_id}%"))
        if age_group:
            query = query.filter(Profile.age_group.ilike(f"%{age_group}%"))
        
        # Apply numeric range filters
        if min_age is not None:
            query = query.filter(Profile.age >= min_age)
        if max_age is not None:
            query = query.filter(Profile.age <= max_age)
        
        # Apply probability filters
        if min_gender_probability is not None:
            query = query.filter(Profile.gender_probability >= min_gender_probability)
        if min_country_probability is not None:
            query = query.filter(Profile.country_probability >= min_country_probability)
        
        # Apply sorting
        if sort_by:
            sort_column = None
            if sort_by.lower() == "age":
                sort_column = Profile.age
            elif sort_by.lower() == "created_at":
                sort_column = Profile.created_at
            elif sort_by.lower() == "gender_probability":
                sort_column = Profile.gender_probability
            
            if sort_column is not None:
                if order.lower() == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        
        return query.offset(skip).limit(limit).all()
    
    def delete_profile(self, profile_id: str):
        """
        Delete a user profile by its unique identifier.
        """
        try:
            profile_uuid = UUID(profile_id)
            profile = self.db.query(Profile).filter(Profile.id == profile_uuid).first()
            if profile:
                self.db.delete(profile)
                self.db.commit()
                return True
            return False
        except (ValueError, TypeError):
            return False
