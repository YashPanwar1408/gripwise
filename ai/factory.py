"""GripWise — AI provider factory."""
from backend.config import settings
from ai.interfaces import InferenceProvider


def get_provider() -> InferenceProvider:
    if settings.INFERENCE_PROVIDER == "mock":
        from ai.providers.mock_provider import MockProvider
        return MockProvider()
    elif settings.INFERENCE_PROVIDER == "cv_pipeline":
        from ai.providers.cv_provider import CVProvider
        return CVProvider()
    raise ValueError(f"Unknown INFERENCE_PROVIDER: {settings.INFERENCE_PROVIDER}")
