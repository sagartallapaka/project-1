from __future__ import annotations

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext
from autorecruiter.core.types import ScreeningResult


class ScreeningAgent(Agent):
    """Score candidate fit for a job."""

    def __init__(self) -> None:
        super().__init__(name="screening")

    def run(self, context: SharedContext) -> SharedContext:
        candidate_profile = context.get("candidate_profile", {})
        job_profile = context.get("job_profile", {})

        score = float(len(set(candidate_profile.get("skills", [])) & set(job_profile.get("required_skills", []))))
        highlights = [f"Matches skill: {skill}" for skill in candidate_profile.get("skills", []) if skill in job_profile.get("required_skills", [])]
        risks = ["Insufficient experience" if candidate_profile.get("experience_years", 0) < context.get("min_experience", 0) else "No major risks"]

        result = ScreeningResult(
            candidate_id=candidate_profile.get("candidate_id", "unknown"),
            job_id=job_profile.get("job_id", context.job_id),
            score=score,
            highlights=highlights,
            risks=risks,
            recommended_action="review" if score > 0 else "reject",
        )

        context.set("screening_result", result.__dict__)
        return context
