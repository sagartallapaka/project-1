from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from autorecruiter.core.context import SharedContext


class Agent(ABC):
    """Abstract base class for all agents."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def run(self, context: SharedContext) -> SharedContext:
        """Execute agent logic and mutate shared context."""


class AgentFactory(Protocol):
    """Factory protocol for creating agents dynamically."""

    def __call__(self, *args, **kwargs) -> Agent:  # type: ignore[override]
        ...
