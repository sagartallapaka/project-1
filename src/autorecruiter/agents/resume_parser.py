from __future__ import annotations

from dataclasses import asdict

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext
from autorecruiter.core.types import CandidateProfile


class ResumeParserAgent(Agent):
    """Parse resumes and extract structured data."""

    def __init__(self) -> None:
        super().__init__(name="resume_parser")

    def run(self, context: SharedContext) -> SharedContext:
        resume_text: str = context.get("resume_text", "")
        candidate_id: str = context.get("candidate_id", "unknown")

        # Placeholder parse logic; to be replaced with NLP pipeline
        profile = CandidateProfile(
            candidate_id=candidate_id,
            name=context.get("candidate_name", "Unknown"),
            email=context.get("candidate_email", "unknown@example.com"),
            phone=context.get("candidate_phone"),
            experience_years=context.get("experience_years", 0.0),
            skills=context.get("skills", []),
            education=context.get("education", []),
            resume_text=resume_text,
            metadata={"source": context.get("resume_source", "upload")},
        )

        context.set("candidate_profile", asdict(profile))
        return context
