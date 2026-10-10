"""GripWise — AI Inference interfaces. Stable protocol: no CV imports here."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Protocol


class ConfidenceTier(str, Enum):
    HIGH = "HIGH_CONFIDENCE"
    MEDIUM = "MEDIUM_CONFIDENCE"
    LOW = "LOW_CONFIDENCE"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class RecommendedAction(str, Enum):
    OK = "ok"
    MONITOR = "monitor"
    INSPECT_SOON = "inspect_soon"
    REPLACE_URGENTLY = "replace_urgently"
    SEEK_MECHANIC_NOW = "seek_mechanic_now"
    ANALYSIS_FAILED = "analysis_failed"


@dataclass
class TyreObservation:
    field: str
    value: Any
    confidence: ConfidenceTier
    explanation: str
    caveat: Optional[str] = None


@dataclass
class InferenceResult:
    provider: str               # "mock" | "cv_pipeline"
    model_version: str
    image_quality: str          # "PASS" | "DEGRADED" | "FAIL"
    quality_issues: list[str]
    detected_tyres: int
    recommended_action: RecommendedAction
    recommended_action_explanation: str
    observations: list[TyreObservation]
    raw_scores: dict
    inference_ms: float


class InferenceProvider(Protocol):
    def analyse(self, image_bytes: bytes) -> InferenceResult: ...
    def health(self) -> dict: ...
