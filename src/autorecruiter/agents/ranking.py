from __future__ import annotations

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext


class RankingAgent(Agent):
    """Rank candidates based on multiple factors."""

    def __init__(self) -> None:
        super().__init__(name="ranking")

    def run(self, context: SharedContext) -> SharedContext:
        screening_results = context.get("screening_result", {})
        fraud_signals = context.get("fraud_signals", [])

        penalty = 10 * len(fraud_signals)
        final_score = screening_results.get("score", 0.0) - penalty

        context.set(
            "ranking_output",
            {
                "final_score": final_score,
                "candidate_id": screening_results.get("candidate_id"),
                "job_id": screening_results.get("job_id", context.job_id),
                "fraud_flags": fraud_signals,
            },
        )
        return context
