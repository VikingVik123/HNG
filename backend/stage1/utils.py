from datetime import datetime

def serialize_profile(profile):
    """
    Serialize a Profile model instance to a dictionary with proper formatting.
    Ensures ISO 8601 UTC timestamps and UUID strings.
    """
    if not profile:
        return None
    
    return {
        "id": str(profile.id),
        "name": profile.name,
        "gender": profile.gender,
        "gender_probability": profile.gender_probability,
        "sample_size": profile.sample_size,
        "age": profile.age,
        "age_group": profile.age_group,
        "country_id": profile.country_id,
        "country_probability": profile.country_probability,
        "created_at": profile.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if isinstance(profile.created_at, datetime) else profile.created_at
    }


def serialize_profile_list(profile):
    """
    Serialize a Profile for list response (subset of fields).
    """
    if not profile:
        return None
    
    return {
        "id": str(profile.id),
        "name": profile.name,
        "gender": profile.gender,
        "age": profile.age,
        "age_group": profile.age_group,
        "country_id": profile.country_id
    }
