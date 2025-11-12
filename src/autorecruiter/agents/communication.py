from __future__ import annotations

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext


class CommunicationAgent(Agent):
    """Generate automated candidate communications."""

    def __init__(self) -> None:
        super().__init__(name="communication")

    def run(self, context: SharedContext) -> SharedContext:
        ranking_output = context.get("ranking_output", {})
        decision_threshold = context.get("decision_threshold", 5)
        final_score = ranking_output.get("final_score", 0)

        if final_score >= decision_threshold:
            message_type = "selection"
            subject = "Interview Invitation"
            body = "Congratulations! We'd like to schedule an interview."
        else:
            message_type = "rejection"
            subject = "Application Update"
            body = "Thank you for applying. We are pursuing other candidates."

        context.set(
            "communication_output",
            {
                "message_type": message_type,
                "subject": subject,
                "body": body,
            },
        )
        return context
