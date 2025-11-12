from __future__ import annotations

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext


class PrivacyGuardAgent(Agent):
    """Enforce privacy and compliance guidelines."""

    def __init__(self) -> None:
        super().__init__(name="privacy_guard")

    def run(self, context: SharedContext) -> SharedContext:
        candidate_profile = context.get("candidate_profile", {})
        approved_fields = context.get("approved_fields", {"name", "email", "skills"})

        sanitized = {
            key: value
            for key, value in candidate_profile.items()
            if key in approved_fields
        }

        context.set("privacy_guard_output", sanitized)
        return context
