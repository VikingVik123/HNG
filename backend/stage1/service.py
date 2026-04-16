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
    
    def get_profiles(self, gender: str = None, country_id: str = None, age_group: str = None, skip: int = 0, limit: int = 100):
        """
        Retrieve a list of user profiles with optional filtering (case-insensitive).
        Supports filtering by: gender, country_id, age_group
        """
        query = self.db.query(Profile)
        
        # Apply filters if provided
        if gender:
            query = query.filter(Profile.gender.ilike(f"%{gender}%"))
        if country_id:
            query = query.filter(Profile.country_id.ilike(f"%{country_id}%"))
        if age_group:
            query = query.filter(Profile.age_group.ilike(f"%{age_group}%"))
        
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
