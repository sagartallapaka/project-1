"""
Job and Job Application models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from . import Base


class JobStatus(str, enum.Enum):
    """Job status enum"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    FILLED = "filled"


class ApplicationStatus(str, enum.Enum):
    """Application status enum"""
    SUBMITTED = "submitted"
    SCREENING = "screening"
    SCREENING_PASSED = "screening_passed"
    SCREENING_FAILED = "screening_failed"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    SELECTED = "selected"
    REJECTED = "rejected"
    OFFER_SENT = "offer_sent"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    HIRED = "hired"
    WITHDRAWN = "withdrawn"


class Job(Base):
    """Job posting model"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)

    # Job Description
    description = Column(Text, nullable=False)
    responsibilities = Column(JSON, nullable=True)  # List of responsibilities
    requirements = Column(JSON, nullable=True)  # List of requirements
    nice_to_have = Column(JSON, nullable=True)  # List of nice-to-have skills

    # Parsed Requirements
    required_skills = Column(JSON, nullable=True)  # Extracted skills from JD
    required_experience_min = Column(Float, nullable=True)
    required_experience_max = Column(Float, nullable=True)
    required_education = Column(JSON, nullable=True)

    # Location & Work Type
    location_city = Column(String(100), nullable=True)
    location_state = Column(String(100), nullable=True)
    location_country = Column(String(100), nullable=False, default="India")
    is_remote = Column(Boolean, default=False)
    work_type = Column(String(20), nullable=True)  # full-time, part-time, contract, internship

    # Compensation
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="INR")

    # Job Details
    job_type = Column(String(50), nullable=True)  # permanent, temporary, internship
    experience_level = Column(String(50), nullable=True)  # entry, mid, senior, lead
    openings = Column(Integer, default=1)

    # Status & Settings
    status = Column(SQLEnum(JobStatus), default=JobStatus.DRAFT, index=True)
    is_published = Column(Boolean, default=False)
    auto_screen = Column(Boolean, default=True)
    auto_reject = Column(Boolean, default=False)

    # Screening Configuration
    screening_criteria = Column(JSON, nullable=True)  # Custom screening rules
    minimum_match_score = Column(Float, default=60.0)

    # Portal Integration
    posted_on_linkedin = Column(Boolean, default=False)
    posted_on_naukri = Column(Boolean, default=False)
    posted_on_indeed = Column(Boolean, default=False)
    posted_on_internshala = Column(Boolean, default=False)

    external_job_ids = Column(JSON, nullable=True)  # {platform: external_id}

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    closing_date = Column(DateTime(timezone=True), nullable=True)
    filled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job {self.title} at {self.company_name}>"


class JobSkill(Base):
    """Required skills for a job"""
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    skill_name = Column(String(100), nullable=False, index=True)
    skill_category = Column(String(50), nullable=True)
    is_required = Column(Boolean, default=True)  # vs nice-to-have
    importance_weight = Column(Float, default=1.0)  # 0-1, for ranking algorithm
    minimum_years = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="skills")

    def __repr__(self):
        return f"<JobSkill {self.skill_name} for Job {self.job_id}>"


class JobApplication(Base):
    """Job application/candidate submission"""
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)

    # Application Info
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, index=True)
    source = Column(String(50), nullable=True)  # direct, linkedin, naukri, etc.
    cover_letter = Column(Text, nullable=True)

    # Screening Results
    match_score = Column(Float, nullable=True)  # 0-100
    ranking_score = Column(Float, nullable=True)  # Overall ranking score
    rank = Column(Integer, nullable=True)  # Rank among all applicants

    screening_passed = Column(Boolean, nullable=True)
    screening_notes = Column(Text, nullable=True)
    screening_details = Column(JSON, nullable=True)  # Detailed analysis

    # Skills Match
    matched_skills = Column(JSON, nullable=True)  # Skills that match
    missing_skills = Column(JSON, nullable=True)  # Required skills missing
    additional_skills = Column(JSON, nullable=True)  # Extra skills candidate has

    # Fake Detection
    fake_likelihood_score = Column(Float, nullable=True)  # 0-1
    fake_detection_flags = Column(JSON, nullable=True)
    is_suspicious = Column(Boolean, default=False)

    # Communication
    last_email_sent = Column(DateTime(timezone=True), nullable=True)
    email_status = Column(String(50), nullable=True)  # sent, opened, clicked

    # Rejection Info
    rejection_reason = Column(Text, nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Selection Info
    selected_at = Column(DateTime(timezone=True), nullable=True)
    selected_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Metadata
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    screened_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    interviews = relationship("Interview", back_populates="application")

    def __repr__(self):
        return f"<JobApplication {self.candidate_id} -> Job {self.job_id} [{self.status.value}]>"
