import pytest
import cv2
import numpy as np
from ai.providers.cv_provider import CVProvider
from ai.interfaces import InferenceResult, RecommendedAction, ConfidenceTier

@pytest.fixture
def dummy_image_bytes():
    # Create a dummy image of sufficient size (224x224) and brightness
    img = np.full((300, 300, 3), 150, dtype=np.uint8)
    
    # Draw a mock tyre shape (circle)
    cv2.circle(img, (150, 150), 100, (50, 50, 50), -1)
    
    # Add some "tread" edges (noise inside the circle)
    noise = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    img[50:250, 50:250] = cv2.addWeighted(img[50:250, 50:250], 0.7, noise, 0.3, 0)
    
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

@pytest.fixture
def corrupt_image_bytes():
    return b"not a real image"

@pytest.fixture
def low_res_image_bytes():
    img = np.full((50, 50, 3), 150, dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

@pytest.fixture
def dark_image_bytes():
    img = np.full((300, 300, 3), 10, dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

def test_cv_provider_success(dummy_image_bytes):
    provider = CVProvider()
    result = provider.analyse(dummy_image_bytes)
    
    assert isinstance(result, InferenceResult)
    assert result.provider == "cv_pipeline"
    assert result.detected_tyres > 0
    assert result.image_quality in ("PASS", "DEGRADED")
    assert result.inference_ms > 0
    
    obs_fields = {o.field for o in result.observations}
    assert "tread_score_proxy" in obs_fields
    assert "anomaly_detected" in obs_fields

def test_cv_provider_corrupt(corrupt_image_bytes):
    provider = CVProvider()
    result = provider.analyse(corrupt_image_bytes)
    
    assert result.image_quality == "FAIL"
    assert "CORRUPT_IMAGE" in result.quality_issues
    assert result.recommended_action == RecommendedAction.ANALYSIS_FAILED

def test_cv_provider_low_res(low_res_image_bytes):
    provider = CVProvider()
    result = provider.analyse(low_res_image_bytes)
    
    assert result.image_quality == "FAIL"
    assert "RESOLUTION_TOO_LOW" in result.quality_issues

def test_cv_provider_dark(dark_image_bytes):
    provider = CVProvider()
    result = provider.analyse(dark_image_bytes)
    
    # Dark images are usually DEGRADED, but depending on threshold could be FAIL
    # Either way, check issues
    assert "TOO_DARK" in result.quality_issues

def test_health():
    provider = CVProvider()
    health = provider.health()
    
    assert health["provider"] == "cv_pipeline"
    assert health["status"] == "healthy"
    assert health["opencv_available"] is True
