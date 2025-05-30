import logging
from datetime import datetime
from typing import List, Optional

from app.models import Job
from app.schemas import (
    JobCreateSchema,
    JobListFilters,
    JobSchema,
    JobUpdateSchema,
    OrderByEnum,
)
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import PageNumberPagination, paginate
from ninja_jwt.authentication import JWTAuth

logger = logging.getLogger(__name__)

router = Router(tags=["Jobs"])  # This is a Router, not a full NinjaAPI

default_auth = JWTAuth()


@router.post("/jobs", response={201: JobSchema}, auth=default_auth)
def create_job(request, payload: JobCreateSchema):
    """
    Create a new job listing.
    """
    logger.info(f"Creating job with payload: {payload.dict()}")
    job = Job(**payload.dict())
    job.save()
    logger.info(f"Job created with ID: {job.id}")
    return job


@router.get("/jobs", response={200: List[JobSchema]}, tags=["Jobs"])
@paginate(PageNumberPagination, page_size=10)
def list_jobs(
    request,
    filters: JobListFilters = Query(default_factory=JobListFilters),
    order_by: Optional[OrderByEnum] = None,
):
    orm_filters = {}
    for name, value in filters.dict(exclude_none=True).items():
        logger.debug(f"Filtering {name}, value: {value}")
        if "required_skills" in name:
            orm_filters[name + "__icontains"] = value
        elif "salary_" in name:
            # salary_gte: filter all jobs that salary_range avg. >= salary_gte
            # salary_lte: filter all jobs that salary_range avg. <= salary_lte
            # if salary_gte and salary_lte are both provided, filter jobs that match both conditions
            if "gte" in name:
                orm_filters["salary_range_avg__gte"] = value
            elif "lte" in name:
                orm_filters["salary_range_avg__lte"] = value
        else:
            orm_filters[name] = value

    logger.debug(f"orm_filters: {orm_filters}")
    jobs = Job.objects.filter(**orm_filters)
    if orm_filters:
        jobs = jobs.filter(**orm_filters)

    search_term = request.GET.get("search", None)  # Example: /jobs?search=developer
    if search_term:
        jobs = jobs.filter(
            Q(title__icontains=search_term)
            | Q(desc__icontains=search_term)
            | Q(company_name__icontains=search_term)
        )

    if order_by:
        jobs = jobs.order_by(order_by.value)
    else:
        jobs = jobs.order_by("-posting_date")  # Default ordering

    for job in Job.objects.filter(
        Q(status="SCHEDULED", posting_date__lte=datetime.now())
        | Q(status="ACTIVE", expiration_date__lt=datetime.now())
    ):
        job.save()  # This will trigger status update logic in the model

    return jobs


@router.get("/jobs/{job_id}", response={200: JobSchema}, tags=["Jobs"])
def get_job(request, job_id: int):
    job = get_object_or_404(Job, id=job_id)
    return job


@router.put("/jobs/{job_id}", response={200: JobSchema}, auth=default_auth)
def update_job(request, job_id: int, payload: JobUpdateSchema):
    job = get_object_or_404(Job, id=job_id)
    logger.info(f"Updating job {job_id} with payload: {payload.dict()}")
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(job, attr, value)
    job.save()
    return job


@router.delete("/jobs/{job_id}", response={204: None}, auth=default_auth)
def delete_job(request, job_id: int):
    job = get_object_or_404(Job, id=job_id)
    job.delete()
    return None
