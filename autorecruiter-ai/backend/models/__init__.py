"""
Database models for AutoRecruiter AI
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

Base = declarative_base()

# Import all models
from .candidate import Candidate, Resume, CandidateSkill
from .job import Job, JobSkill, JobApplication
from .interview import Interview, InterviewFeedback
from .user import User, Role
from .audit import AuditLog

__all__ = [
    "Base",
    "Candidate",
    "Resume",
    "CandidateSkill",
    "Job",
    "JobSkill",
    "JobApplication",
    "Interview",
    "InterviewFeedback",
    "User",
    "Role",
    "AuditLog",
]
