from __future__ import annotations

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext
from autorecruiter.core.types import FraudSignal


class FraudDetectorAgent(Agent):
    """Detect fake claims and anomalies."""

    def __init__(self) -> None:
        super().__init__(name="fraud_detector")

    def run(self, context: SharedContext) -> SharedContext:
        candidate_profile = context.get("candidate_profile", {})
        job_profile = context.get("job_profile", {})

        signals: list[FraudSignal] = []

        if candidate_profile.get("experience_years", 0) < context.get("claimed_experience", 0):
            signals.append(
                FraudSignal(
                    candidate_id=candidate_profile.get("candidate_id", "unknown"),
                    job_id=job_profile.get("job_id", context.job_id),
                    signal_type="experience_mismatch",
                    severity="high",
                    details="Claimed experience exceeds parsed years.",
                )
            )

        context.set("fraud_signals", [signal.__dict__ for signal in signals])
        return context
