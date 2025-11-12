from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SharedContext:
    """Context object passed between agents."""

    job_id: str
    data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any | None = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def merge(self, payload: Dict[str, Any]) -> None:
        self.data.update(payload)
