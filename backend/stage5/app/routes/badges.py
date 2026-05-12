from fastapi import APIRouter, Request

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
def get_job(job_id: str, request: Request):

    db = SessionLocal()

    try:
        job = db.query(BadgeGenerationJob).filter(
            BadgeGenerationJob.job_id == job_id
        ).first()

        if not job:
            db.close()
            return {"error": "not found"}

        # Construct full URL for badge_image_url if it exists
        badge_url = job.badge_image_url
        if badge_url:
            badge_url = str(request.base_url).rstrip('/') + badge_url

        db.close()

        return {
            "job_id": str(job.job_id),
            "status": job.status.value,
            "badge_image_url": badge_url,
            "error_message": job.error_message
        }
    except Exception as e:
        db.close()
        return {"error": f"invalid request: {str(e)}"}