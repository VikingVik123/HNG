from fastapi import APIRouter
import uuid

from app.schemas.badge import BadgeGenerateRequest
from app.db.session import SessionLocal
from app.models.badge_job import BadgeGenerationJob
from app.services.queue import badge_queue
from app.workers.badge_worker import process_badge_generation
from app.enums.job_status import JobStatus

router = APIRouter()


@router.post("/badges/generate")
def generate_badge(payload: BadgeGenerateRequest):

    db = SessionLocal()

    job = BadgeGenerationJob(
        template_id=payload.template_id,
        participant_name=payload.participant_name,
        participant_photo_url=payload.photo_url,
        status=JobStatus.QUEUED
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    badge_queue.enqueue(
        process_badge_generation,
        str(job.job_id)
    )

    db.close()

    return {
        "job_id": str(job.job_id),
        "status": job.status.value
    }


@router.get("/badges/jobs/{job_id}")
def get_job(job_id: str):

    db = SessionLocal()

    try:
        # Convert string job_id to UUID
        job_uuid = uuid.UUID(job_id)
        
        job = db.query(BadgeGenerationJob).filter(
            BadgeGenerationJob.job_id == job_uuid
        ).first()

        if not job:
            return {"error": "not found"}

        db.close()

        return {
            "job_id": str(job.job_id),
            "status": job.status.value,
            "badge_image_url": job.badge_image_url,
            "error_message": job.error_message
        }
    except ValueError:
        db.close()
        return {"error": "invalid job_id format"}