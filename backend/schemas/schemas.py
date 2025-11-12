from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.models import ApplicationStatus, JobStatus


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "recruiter"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job Schemas
class JobBase(BaseModel):
    title: str
    description: str
    requirements: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    deadline: Optional[datetime] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: Optional[JobStatus] = None
    deadline: Optional[datetime] = None


class JobResponse(JobBase):
    id: int
    status: JobStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Candidate Schemas
class CandidateBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: int
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_history: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[str]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Application Schemas
class ApplicationCreate(BaseModel):
    job_id: int
    candidate_id: int


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    status: ApplicationStatus
    screening_score: Optional[float] = None
    screening_notes: Optional[str] = None
    skill_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    fake_detection_score: Optional[float] = None
    fake_detection_flags: Optional[List[str]] = None
    is_verified: bool
    overall_rank: Optional[int] = None
    ranking_score: Optional[float] = None
    interview_scheduled_at: Optional[datetime] = None
    applied_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationWithDetails(ApplicationResponse):
    job: JobResponse
    candidate: CandidateResponse


# Resume Upload
class ResumeUploadResponse(BaseModel):
    candidate_id: int
    parsed_data: Dict[str, Any]
    message: str


# Screening Result
class ScreeningResult(BaseModel):
    application_id: int
    screening_score: float
    skill_match_score: float
    experience_match_score: float
    education_match_score: float
    screening_notes: str
    recommended_action: str  # shortlist, reject, review


# Fake Detection Result
class FakeDetectionResult(BaseModel):
    application_id: int
    fake_detection_score: float
    is_suspicious: bool
    flags: List[str]
    details: Dict[str, Any]


# Ranking Result
class RankingResult(BaseModel):
    application_id: int
    ranking_score: float
    rank: int
    strengths: List[str]
    weaknesses: List[str]


# Chat Message
class ChatMessageCreate(BaseModel):
    candidate_id: int
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    candidate_id: int
    message: str
    response: Optional[str] = None
    is_from_candidate: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Email Template
class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    body: str
    template_type: str
    variables: Optional[List[str]] = None


class EmailTemplateResponse(EmailTemplateCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analytics
class JobAnalytics(BaseModel):
    job_id: int
    total_applications: int
    screening_in_progress: int
    shortlisted: int
    interviewed: int
    selected: int
    rejected: int
    average_screening_score: float
    average_ranking_score: float
    top_skills: List[Dict[str, Any]]


# Plugin API
class PluginJobPosting(BaseModel):
    external_job_id: str
    portal_name: str  # linkedin, naukri, indeed, internshala
    job_data: JobCreate


class PluginApplicationWebhook(BaseModel):
    external_application_id: str
    external_job_id: str
    portal_name: str
    candidate_data: CandidateCreate
    resume_url: Optional[str] = None
