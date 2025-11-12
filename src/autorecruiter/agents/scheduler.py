from __future__ import annotations

from datetime import datetime, timedelta

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext
from autorecruiter.core.types import InterviewProposal, InterviewSlot


class SchedulerAgent(Agent):
    """Propose interview times based on availability."""

    def __init__(self) -> None:
        super().__init__(name="scheduler")

    def run(self, context: SharedContext) -> SharedContext:
        candidate_availability = context.get("candidate_availability", [])
        recruiter_availability = context.get("recruiter_availability", [])

        proposed_slots: list[InterviewSlot] = []
        now = datetime.utcnow()
        for i in range(3):
            start_time = now + timedelta(days=i + 1)
            end_time = start_time + timedelta(hours=1)
            proposed_slots.append(
                InterviewSlot(start_time=start_time, end_time=end_time, timezone="UTC")
            )

        proposal = InterviewProposal(
            candidate_id=context.get("candidate_id", "unknown"),
            job_id=context.job_id,
            proposed_slots=proposed_slots,
            status="pending",
        )

        context.set("scheduler_output", proposal.__dict__)
        return context
