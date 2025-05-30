from datetime import date, datetime
from enum import Enum
from typing import Optional

from ninja import Field, Schema
from pydantic import field_validator


class JobBaseSchema(Schema):
    title: str = Field(..., min_length=3, max_length=255)
    desc: Optional[str] = Field(None, min_length=10, max_length=1000)
    location: Optional[str] = Field(None, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    company_name: str = Field(..., min_length=1, max_length=255)
    posting_date: date = Field(default_factory=date.today)
    expiration_date: Optional[date] = Field(None)
    required_skills: Optional[str] = Field(None)

    @field_validator("salary_range")
    @classmethod
    def validate_salary_range(cls, value):
        if value:
            if value == "面議":
                return value
            parts = value.split("~")
            if len(parts) != 2:
                if value.isdigit():
                    return f"{value}~{value}"
                else:
                    raise ValueError('salary_range must be in the format "min-max"')
            try:
                min_salary, max_salary = map(float, parts)
                if min_salary < 0 or max_salary < 0:
                    raise ValueError("salary_range values must be non-negative")
                if min_salary > max_salary:
                    raise ValueError("salary_range min cannot be greater than max")
            except ValueError:
                raise ValueError("salary_range must contain valid numeric values")
        return value

    @field_validator("required_skills")
    @classmethod
    def validate_required_skills(cls, value):
        if value and len(value.split(",")) > 10:
            raise ValueError("required_skills cannot exceed 10 skills")
        return value


class JobCreateSchema(JobBaseSchema):
    pass


class JobUpdateSchema(Schema):
    title: Optional[str] = Field(None, min_length=3)
    desc: Optional[str] = Field(None, min_length=10)


class JobSchema(JobBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    status: Optional[str] = Field(None, max_length=10)


class JobListFilters(Schema):
    """
    Filter by location, salary_range, posting_date, expiration_date, required_skills
    Filter by status
    """

    location: Optional[str] = Field(None, min_length=1, max_length=255)
    salary_gte: Optional[str] = Field(None, max_length=100)
    salary_lte: Optional[str] = Field(None, max_length=100)
    posting_date__gte: Optional[date] = Field(None)
    posting_date__lte: Optional[date] = Field(None)
    expiration_date__gte: Optional[date] = Field(None)
    expiration_date__lte: Optional[date] = Field(None)
    required_skills: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=10)

    @field_validator("salary_gte", "salary_lte")
    @classmethod
    def validate_salary(cls, value):
        if value:
            try:
                int(value)  # Ensure it's a valid number
            except ValueError:
                raise ValueError("salary_gte and salary_lte must be valid numbers")
        return value


class OrderByEnum(str, Enum):
    posting_date_asc = "posting_date"
    posting_date_desc = "-posting_date"
    expiration_date_asc = "expiration_date"
    expiration_date_desc = "-expiration_date"
