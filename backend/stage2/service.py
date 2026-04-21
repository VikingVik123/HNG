import httpx
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
import os
import re
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
        page: int = 1,
        limit: int = 10
    ):
        """
        Retrieve a list of user profiles with advanced optional filtering, sorting, and pagination.
        """
        query = self.db.query(Profile)
        
        # Apply categorical filters (case-insensitive exact match, not partial)
        if gender:
            query = query.filter(Profile.gender.ilike(gender))
        if country_id:
            query = query.filter(Profile.country_id.ilike(country_id))
        if age_group:
            query = query.filter(Profile.age_group.ilike(age_group))
        
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
        
        # Get total count before pagination
        total = query.count()
        
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
        
        # Apply pagination
        skip = (page - 1) * limit
        profiles = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "data": profiles
        }
    
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
    
    def parse_natural_language_query(self, query: str):
        """
        Parse natural language query and convert to filters using rule-based parsing.
        
        Returns: dict with filter parameters or None if unable to interpret
        
        Example mappings:
        "young males" → gender=male + min_age=16 + max_age=24
        "females above 30" → gender=female + min_age=30
        "people from angola" → country_id=AO
        "adult males from kenya" → gender=male + age_group=adult + country_id=KE
        "male and female teenagers above 17" → age_group=teenager + min_age=17
        """
        if not query or not isinstance(query, str):
            return None
        
        query_lower = query.lower().strip()
        filters = {}
        
        # Country mapping (name to country code)
        country_map = {
            "nigeria": "NG", "nigerian": "NG",
            "kenya": "KE", "kenyan": "KE",
            "south africa": "ZA", "south african": "ZA",
            "ghana": "GH", "ghanaian": "GH",
            "uganda": "UG", "ugandan": "UG",
            "tanzania": "TZ", "tanzanian": "TZ",
            "ethiopia": "ET", "ethiopian": "ET",
            "cameroon": "CM", "cameroonian": "CM",
            "angola": "AO", "angolan": "AO",
            "mozambique": "MZ", "mozambican": "MZ",
            "zambia": "ZM", "zambian": "ZM",
            "zimbabwe": "ZW", "zimbabwean": "ZW",
            "botswana": "BW", "batswana": "BW",
            "namibia": "NA", "namibian": "NA",
            "malawi": "MW", "malawian": "MW",
            "senegal": "SN", "senegalese": "SN",
            "ivory coast": "CI", "côte d'ivoire": "CI",
            "united states": "US", "usa": "US", "american": "US",
            "united kingdom": "GB", "uk": "GB", "british": "GB",
            "canada": "CA", "canadian": "CA",
            "australia": "AU", "australian": "AU",
            "india": "IN", "indian": "IN",
            "china": "CN", "chinese": "CN",
        }
        
        # Gender mapping
        gender_keywords = {
            "male": "male", "man": "male", "boy": "male", "men": "male", "boys": "male",
            "female": "female", "woman": "female", "girl": "female", "women": "female", "girls": "female"
        }
        
        # Age group keywords
        age_group_keywords = {
            "teenager": "teenager", "teen": "teenager", "teenagers": "teenager", "teens": "teenager",
            "adult": "adult", "adults": "adult",
            "child": "child", "children": "child", "kid": "child", "kids": "child",
            "senior": "senior", "seniors": "senior", "elderly": "senior"
        }
        
        # Extract country
        for country_name, country_code in country_map.items():
            if country_name in query_lower:
                filters["country_id"] = country_code
                query_lower = query_lower.replace(country_name, "")
                break
        
        # Extract gender - handle "male and female" with word boundary matching
        # Check for female keywords (including plural forms) - use word boundaries
        female_keywords = ["female", "females", "woman", "women", "girl", "girls"]
        male_keywords = ["male", "males", "man", "men", "boy", "boys"]
        
        # Use regex with word boundaries to match whole words only
        has_female = any(re.search(r'\b' + keyword + r'\b', query_lower) for keyword in female_keywords)
        has_male = any(re.search(r'\b' + keyword + r'\b', query_lower) for keyword in male_keywords)
        
        if has_male and has_female:
            # Both genders specified, don't filter by gender
            pass
        elif has_male:
            filters["gender"] = "male"
        elif has_female:
            filters["gender"] = "female"
        
        # Extract age group
        for keyword, age_group in age_group_keywords.items():
            if keyword in query_lower:
                filters["age_group"] = age_group
                break
        
        # Extract numeric ages and modifiers
        # Pattern to find numbers in the query
        numbers = re.findall(r'\b(\d+)\b', query_lower)
        
        if numbers:
            age_num = int(numbers[0])
            
            # Check for modifiers before the number
            if any(mod in query_lower for mod in ["above", "older than", "over", "more than", "at least", "above"]):
                # Extract the position of "above" or similar
                if "above" in query_lower:
                    idx = query_lower.index("above")
                    # Check if number comes after "above"
                    if query_lower[idx:].find(str(age_num)) != -1:
                        filters["min_age"] = age_num
                elif "older than" in query_lower or "over" in query_lower or "more than" in query_lower or "at least" in query_lower:
                    filters["min_age"] = age_num
            elif any(mod in query_lower for mod in ["below", "younger than", "under", "less than"]):
                if "below" in query_lower:
                    idx = query_lower.index("below")
                    if query_lower[idx:].find(str(age_num)) != -1:
                        filters["max_age"] = age_num
                elif "younger than" in query_lower or "under" in query_lower or "less than" in query_lower:
                    filters["max_age"] = age_num
            else:
                # Just a number without modifier
                filters["min_age"] = age_num
        
        # Handle "young" keyword - maps to ages 16-24
        if "young" in query_lower:
            if "min_age" not in filters:
                filters["min_age"] = 16
            if "max_age" not in filters:
                filters["max_age"] = 24
        
        # Handle "old" or "older" keyword
        if ("old" in query_lower or "older" in query_lower) and "min_age" not in filters:
            # Default to 40+ if no specific age given
            filters["min_age"] = 40
        
        # Validate that we found at least some meaningful filter
        if not filters or (len(filters) == 0):
            return None
        
        return filters
    
    def get_profiles_by_query(
        self,
        query: str,
        page: int = 1,
        limit: int = 10
    ):
        """
        Retrieve profiles by natural language query.
        
        Returns: dict with 'total', 'data', 'filters_used' keys, or None if query couldn't be parsed
        """
        filters = self.parse_natural_language_query(query)
        
        if filters is None:
            return None
        
        # Call get_profiles with the parsed filters
        result = self.get_profiles(
            gender=filters.get("gender"),
            country_id=filters.get("country_id"),
            age_group=filters.get("age_group"),
            min_age=filters.get("min_age"),
            max_age=filters.get("max_age"),
            page=page,
            limit=limit
        )
        
        # Add filters_used to the result
        result["filters_used"] = filters
        
        return result
