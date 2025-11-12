from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CandidateProfile:
    candidate_id: str
    name: str
    email: str
    phone: Optional[str]
    experience_years: float
    skills: List[str]
    education: List[str]
    resume_text: str
    metadata: Dict[str, Any]


@dataclass
class JobProfile:
    job_id: str
    title: str
    department: Optional[str]
    required_skills: List[str]
    responsibilities: List[str]
    preferred_qualifications: List[str]
    salary_range: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class ScreeningResult:
    candidate_id: str
    job_id: str
    score: float
    highlights: List[str]
    risks: List[str]
    recommended_action: str


@dataclass
class FraudSignal:
    candidate_id: str
    job_id: str
    signal_type: str
    severity: str
    details: str


@dataclass
class InterviewSlot:
    start_time: datetime
    end_time: datetime
    timezone: str


@dataclass
class InterviewProposal:
    candidate_id: str
    job_id: str
    proposed_slots: List[InterviewSlot]
    status: str
