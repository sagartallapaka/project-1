from __future__ import annotations

from dataclasses import asdict

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext
from autorecruiter.core.types import JobProfile


class JobAnalysisAgent(Agent):
    """Analyze job descriptions to extract requirements."""

    def __init__(self) -> None:
        super().__init__(name="job_analysis")

    def run(self, context: SharedContext) -> SharedContext:
        jd_text: str = context.get("job_description", "")
        job_id: str = context.job_id

        profile = JobProfile(
            job_id=job_id,
            title=context.get("job_title", "Unknown"),
            department=context.get("job_department"),
            required_skills=context.get("required_skills", []),
            responsibilities=context.get("responsibilities", []),
            preferred_qualifications=context.get("preferred_qualifications", []),
            salary_range=context.get("salary_range"),
            metadata={"source": context.get("jd_source", "upload"), "raw_text": jd_text},
        )

        context.set("job_profile", asdict(profile))
        return context
