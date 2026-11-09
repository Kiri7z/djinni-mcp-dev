"""The public tool result contract; unknown source values remain null."""

from typing import Any, Literal

from pydantic import BaseModel

Category = Literal["Sysadmin", "DevOps", "Lead", "Head Chief", "Support"]
CompanyType = Literal["product", "outsource", "outstaff", "agency", "startup"]
Activity = Literal["open", "closed", "unknown"]


class JobSummary(BaseModel):
    id: str
    url: str
    title: str
    categories: list[str]
    source_pub_date: str | None
    activity: Literal["unknown"] = "unknown"
    activity_checked_at: None = None
    previously_recommended_at: str | None = None


class SearchResult(BaseModel):
    contract_version: str = "0.1"
    checked_at: str
    source_url: str
    coverage: Literal["unknown"] = "unknown"
    possibly_truncated: bool
    fetched_count: int
    matched_count: int
    returned_count: int
    next_offset: int | None
    jobs: list[JobSummary]
    warnings: list[str]


class SourceDates(BaseModel):
    source_date_posted: str | None = None
    source_valid_through: str | None = None
    published_label: str | None = None
    updated_label: str | None = None


class JobDetail(BaseModel):
    id: str
    url: str
    title: str
    company: str | None
    description: str | None
    description_truncated: bool
    description_length: int
    categories: list[str]
    work_format: str | None
    eligible_locations: str | dict[str, Any] | list[Any] | None
    english_requirement: str | None
    salary: dict[str, Any] | None
    dates: SourceDates
    activity: Activity
    activity_checked_at: str


class DetailResult(BaseModel):
    contract_version: str = "0.1"
    checked_at: str
    job: JobDetail
    warnings: list[str]
