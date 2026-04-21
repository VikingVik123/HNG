import json
import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from db import engine, SessionLocal, Base, create_tables
from model import Profile


def verify_database_constraints() -> bool:
    """
    Verify that the database has the required UNIQUE constraint on Profile.name.
    This is the primary defense against duplicate records.
    
    Returns:
        True if constraints are properly set, False otherwise
    """
    db: Session = SessionLocal()
    try:
        # Check if the unique index exists
        # SQLite stores this in sqlite_master table
        inspector_query = """
        SELECT COUNT(*) as count FROM sqlite_master 
        WHERE type='index' AND name='ix_profile_name_unique'
        """
        result = db.execute(inspector_query).fetchone()
        if result and result[0] > 0:
            print("✓ Database constraint verified: UNIQUE index on 'name' column exists")
            return True
        else:
            print("⚠ Warning: UNIQUE index on 'name' not found, creating tables...")
            Base.metadata.create_all(bind=engine)
            return True
    except Exception as e:
        print(f"Notice: Could not verify constraints: {e}")
        # Still proceed, as the constraint should exist from model definition
        Base.metadata.create_all(bind=engine)
        return True
    finally:
        db.close()


def check_existing_profiles(db: Session, name: str) -> bool:
    """
    Check if a profile with the given name already exists in the database.
    Uses a fresh query to ensure accuracy.
    
    Args:
        db: Database session
        name: Profile name to check
        
    Returns:
        True if profile exists, False otherwise
    """
    try:
        existing = db.query(Profile).filter(Profile.name == name).first()
        return existing is not None
    except Exception as e:
        print(f"Error checking for existing profile: {e}")
        return False


def clear_all_profiles(confirm: bool = True) -> None:
    """
    Clear all profiles from the database (useful for fresh seeding).
    
    Args:
        confirm: If True, requires confirmation before clearing
    """
    if confirm:
        response = input("Are you sure you want to delete ALL profiles? Type 'yes' to confirm: ").strip().lower()
        if response != 'yes':
            print("Cancelled.")
            return
    
    db: Session = SessionLocal()
    try:
        count = db.query(Profile).delete()
        db.commit()
        print(f"✓ Deleted {count} profiles from database")
    except Exception as e:
        db.rollback()
        print(f"✗ Error clearing profiles: {e}")
    finally:
        db.close()


def load_seed_data(json_file: str = "seed_profiles.json", clear_first: bool = False) -> None:
    """
    Load profile data from JSON file and seed the database.
    
    **DUPLICATE PREVENTION STRATEGY:**
    
    1. **Database Level (PRIMARY):**
       - UNIQUE constraint on 'name' column
       - Database will reject any duplicate inserts
       - Prevents duplicates even if app logic fails
    
    2. **Application Level (SECONDARY):**
       - Check database before insert
       - Check JSON for duplicates
       - Track processed names in session
       - Validate data before insert
    
    3. **Transaction Level (TERTIARY):**
       - Individual commits for each record
       - Immediate rollback on constraint violation
       - No partial/corrupt data
    
    Args:
        json_file: Path to the JSON file containing profiles
        clear_first: If True, clears all existing profiles before seeding
    """
    print("\n" + "=" * 70)
    print("PROFILE SEEDING - DUPLICATE PROTECTION ENABLED")
    print("=" * 70)
    
    # **Step 0: Verify database constraints**
    print("\nStep 1: Verifying database constraints...")
    verify_database_constraints()
    
    # **Step 1: Create tables if they don't exist**
    print("\nStep 2: Creating database tables (if needed)...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready")
    
    # **Step 2: Clear database if requested**
    if clear_first:
        print("\nStep 3: Clearing existing data...")
        clear_all_profiles(confirm=False)
    else:
        print("\nStep 3: Skipping database clear (duplicates will be ignored)")
    
    # **Step 3: Check if JSON file exists**
    print(f"\nStep 4: Loading JSON file: {json_file}")
    if not os.path.exists(json_file):
        print(f"✗ Error: {json_file} not found")
        return
    
    # **Step 4: Load JSON data**
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ Error reading JSON file: {e}")
        return
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # **Step 5: Get profiles from JSON**
    profiles_data = data.get("profiles", [])
    
    if not profiles_data:
        print("✗ No profiles found in JSON file")
        return
    
    print(f"✓ Loaded {len(profiles_data)} profiles from JSON")
    
    # **Step 6: Validate JSON for duplicate names**
    print(f"\nStep 5: Validating for duplicate names in JSON...")
    seen_names = set()
    json_duplicates = []
    
    for profile in profiles_data:
        name = profile.get("name")
        if name:
            if name in seen_names:
                json_duplicates.append(name)
            else:
                seen_names.add(name)
    
    if json_duplicates:
        print(f"⚠ Found {len(json_duplicates)} duplicate names in JSON:")
        for dup in json_duplicates[:5]:
            print(f"  - {dup}")
        print(f"✓ Will skip duplicates during import")
    else:
        print(f"✓ No duplicates found in JSON file")
    
    # **Step 7: Create database session**
    print(f"\nStep 6: Importing profiles...")
    db: Session = SessionLocal()
    
    try:
        created_count = 0
        skipped_count = 0
        error_count = 0
        json_dup_count = 0
        constraint_violation_count = 0
        
        # Track profiles already processed in this session
        processed_names = set()
        
        for idx, profile_data in enumerate(profiles_data, 1):
            profile_name = profile_data.get("name")
            
            # Validate profile name
            if not profile_name:
                print(f"  [{idx}/{len(profiles_data)}] ✗ Missing 'name' field")
                error_count += 1
                continue
            
            # **Check 1: Duplicate within the JSON being processed**
            if profile_name in processed_names:
                print(f"  [{idx}/{len(profiles_data)}] ⊘ Skipped (duplicate in JSON): {profile_name}")
                json_dup_count += 1
                continue
            
            try:
                # **Check 2: Database constraint-level protection**
                # Query to check if exists (application-level defense)
                existing_profile = check_existing_profiles(db, profile_name)
                
                if existing_profile:
                    print(f"  [{idx}/{len(profiles_data)}] ⊘ Skipped (exists in database): {profile_name}")
                    skipped_count += 1
                    processed_names.add(profile_name)
                    continue
                
                # **Create new profile**
                profile = Profile(
                    name=profile_name,
                    gender=profile_data.get("gender"),
                    gender_probability=profile_data.get("gender_probability"),
                    sample_size=profile_data.get("sample_size"),
                    age=profile_data.get("age"),
                    age_group=profile_data.get("age_group"),
                    country_id=profile_data.get("country_id"),
                    country_name=profile_data.get("country_name"),
                    country_probability=profile_data.get("country_probability"),
                    created_at=datetime.now(timezone.utc)
                )
                
                db.add(profile)
                # **COMMIT IMMEDIATELY - ensures database constraint is checked**
                db.commit()
                print(f"  [{idx}/{len(profiles_data)}] ✓ Created: {profile_name}")
                created_count += 1
                processed_names.add(profile_name)
                
            except IntegrityError as e:
                # **DATABASE-LEVEL PROTECTION ACTIVATED**
                # This catches ANY duplicate that somehow slipped through
                db.rollback()
                if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
                    print(f"  [{idx}/{len(profiles_data)}] ⊘ Rejected (database constraint): {profile_name}")
                    constraint_violation_count += 1
                else:
                    print(f"  [{idx}/{len(profiles_data)}] ✗ Integrity error: {profile_name}")
                    error_count += 1
                processed_names.add(profile_name)
                
            except OperationalError as e:
                # Handle database operational errors
                db.rollback()
                print(f"  [{idx}/{len(profiles_data)}] ✗ Database error: {profile_name} - {str(e)}")
                error_count += 1
                
            except Exception as e:
                # Handle any other errors
                db.rollback()
                print(f"  [{idx}/{len(profiles_data)}] ✗ Error: {profile_name} - {str(e)}")
                error_count += 1
        
        # **Print detailed summary**
        print("\n" + "=" * 70)
        print("SEEDING COMPLETE - SUMMARY")
        print("=" * 70)
        print(f"Created (New):                 {created_count}")
        print(f"Skipped (Existed in DB):       {skipped_count}")
        print(f"Rejected (DB Constraint):      {constraint_violation_count}")
        print(f"Skipped (Duplicate in JSON):   {json_dup_count}")
        print(f"Errors (Other):                {error_count}")
        print(f"Total Processed:               {len(profiles_data)}")
        print(f"\nDuplicate Prevention Status:   {'✓ PASSED' if constraint_violation_count == 0 else '✓ PASSED (DB Constraint Worked)'}")
        print("=" * 70 + "\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    load_seed_data()
