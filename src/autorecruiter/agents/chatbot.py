from __future__ import annotations

from autorecruiter.agents.base import Agent
from autorecruiter.core.context import SharedContext


class ChatbotAgent(Agent):
    """Handle candidate and recruiter queries."""

    def __init__(self) -> None:
        super().__init__(name="chatbot")

    def run(self, context: SharedContext) -> SharedContext:
        faq = context.get("faq", {})
        context.set("chatbot_output", {"responses": faq})
        return context
