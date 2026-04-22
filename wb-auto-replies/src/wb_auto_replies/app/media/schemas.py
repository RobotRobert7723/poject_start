from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VisionSummaryResult:
    summary: str
    confidence: float
    status: str
