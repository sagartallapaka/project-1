"""
Candidate and Resume models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base


class Candidate(Base):
    """Candidate model"""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # Location
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)

    # Profile
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)

    # Professional Info
    current_company = Column(String(255), nullable=True)
    current_designation = Column(String(255), nullable=True)
    total_experience_years = Column(Float, default=0.0)

    # Education
    highest_education = Column(String(100), nullable=True)
    university = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Metadata
    source = Column(String(50), nullable=True)  # linkedin, naukri, indeed, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Candidate {self.first_name} {self.last_name} ({self.email})>"


class Resume(Base):
    """Resume model - stores parsed resume data"""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    # File Info
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(10), nullable=True)  # pdf, docx, etc.

    # Parsed Content
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)  # Complete structured JSON

    # Extracted Information
    summary = Column(Text, nullable=True)
    work_experience = Column(JSON, nullable=True)  # List of jobs
    education = Column(JSON, nullable=True)  # List of degrees
    skills = Column(JSON, nullable=True)  # List of skills
    certifications = Column(JSON, nullable=True)  # List of certifications
    projects = Column(JSON, nullable=True)  # List of projects
    languages = Column(JSON, nullable=True)  # List of languages

    # Analysis Results
    fake_detection_score = Column(Float, nullable=True)  # 0-1, higher = more suspicious
    fake_detection_flags = Column(JSON, nullable=True)  # List of detected issues
    quality_score = Column(Float, nullable=True)  # Resume quality 0-100

    # Processing Status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)

    # Metadata
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    is_latest = Column(Boolean, default=True)  # Mark the latest resume

    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")

    def __repr__(self):
        return f"<Resume {self.filename} for Candidate {self.candidate_id}>"


class CandidateSkill(Base):
    """Candidate skills with proficiency levels"""
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    skill_name = Column(String(100), nullable=False, index=True)
    skill_category = Column(String(50), nullable=True)  # technical, soft, language, etc.
    proficiency_level = Column(String(20), nullable=True)  # beginner, intermediate, expert
    years_of_experience = Column(Float, nullable=True)

    # Verification
    is_verified = Column(Boolean, default=False)
    verification_source = Column(String(100), nullable=True)  # resume, linkedin, certification

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="skills")

    def __repr__(self):
        return f"<CandidateSkill {self.skill_name} - {self.proficiency_level}>"
