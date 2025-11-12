from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    SCREENING = "screening"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    SELECTED = "selected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="recruiter")  # admin, recruiter, interviewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    jobs = relationship("Job", back_populates="created_by_user")


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(JSON)  # List of required skills, experience, etc.
    location = Column(String(255))
    job_type = Column(String(50))  # full-time, part-time, contract, internship
    experience_min = Column(Integer)  # in years
    experience_max = Column(Integer)
    salary_min = Column(Float)
    salary_max = Column(Float)
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deadline = Column(DateTime(timezone=True))
    
    created_by_user = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    location = Column(String(255))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    
    # Parsed resume data
    skills = Column(JSON)  # List of skills
    experience_years = Column(Float)
    education = Column(JSON)  # List of education entries
    work_history = Column(JSON)  # List of work experiences
    certifications = Column(JSON)  # List of certifications
    projects = Column(JSON)  # List of projects
    
    # Resume file
    resume_path = Column(String(500))
    resume_text = Column(Text)  # Extracted text
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    applications = relationship("Application", back_populates="candidate")


class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED)
    
    # Screening results
    screening_score = Column(Float)  # 0-100
    screening_notes = Column(Text)
    skill_match_score = Column(Float)
    experience_match_score = Column(Float)
    education_match_score = Column(Float)
    
    # Fake detection
    fake_detection_score = Column(Float)  # 0-100, higher = more likely fake
    fake_detection_flags = Column(JSON)  # List of detected issues
    is_verified = Column(Boolean, default=False)
    
    # Ranking
    overall_rank = Column(Integer)
    ranking_score = Column(Float)  # Final composite score
    
    # Interview
    interview_scheduled_at = Column(DateTime(timezone=True))
    interview_notes = Column(Text)
    interview_feedback = Column(JSON)
    
    # Communication
    emails_sent = Column(JSON)  # Log of emails sent
    last_email_sent_at = Column(DateTime(timezone=True))
    
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)  # view_resume, download_data, etc.
    resource_type = Column(String(50))  # candidate, application, job
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    message = Column(Text, nullable=False)
    response = Column(Text)
    is_from_candidate = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmailTemplate(Base):
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    template_type = Column(String(50))  # application_received, shortlisted, rejected, interview_invite, selected
    variables = Column(JSON)  # List of available variables
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
