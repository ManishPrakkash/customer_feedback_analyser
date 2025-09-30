"""Define the shared values."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class State:
    """Main graph state."""

    feedback: str = ""
    """The customer feedback provided from the user for analysis."""
    
    category: str = ""
    """The category of the feedback analyzed by the ai agent."""
    
    entities: List[str] = field(default_factory=list)
    """The entities extracted from the feedback."""

    summary: str = ""
    """A summary of the feedback."""

    sentiment: str = ""
    """The sentiment of the feedback."""

    priority: str = ""
    """The priority assigned to the feedback."""

    route: str = ""
    """The route based on the feedback category."""

    action_items: List[str] = field(default_factory=list)
    """The action items generated from the feedback."""

    trend_analysis: str = ""
    """The result of the trend analysis."""


__all__ = [
    "State",
]