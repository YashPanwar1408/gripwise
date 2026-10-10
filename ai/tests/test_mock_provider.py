"""GripWise AI Tests — Mock provider correctness."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from ai.providers.mock_provider import MockProvider
from ai.interfaces import ConfidenceTier, InferenceResult


SMALL_IMG = b"small"
VALID_IMG = b"valid image bytes" * 200   # > 1KB


def test_returns_inference_result():
    result = MockProvider().analyse(VALID_IMG)
    assert isinstance(result, InferenceResult)


def test_provider_is_labelled_mock():
    result = MockProvider().analyse(VALID_IMG)
    assert result.provider == "mock"


def test_every_observation_has_confidence_tier():
    result = MockProvider().analyse(VALID_IMG)
    valid_tiers = {t.value for t in ConfidenceTier}
    for obs in result.observations:
        assert obs.confidence.value in valid_tiers


def test_tread_score_observation_has_caveat():
    for seed in [b"A" * 200, b"B" * 200, b"C" * 200, b"D" * 200]:
        result = MockProvider().analyse(seed)
        tread_obs = [o for o in result.observations if o.field == "tread_score"]
        if tread_obs and tread_obs[0].value is not None:
            assert tread_obs[0].caveat is not None
            assert len(tread_obs[0].caveat) > 20


def test_no_safe_unsafe_verdict():
    for seed in [b"A" * 200, b"B" * 200, b"C" * 200]:
        result = MockProvider().analyse(seed)
        all_text = str(result).lower()
        assert "your tyre is safe" not in all_text
        assert "your tyre is unsafe" not in all_text


def test_quality_fail_on_tiny_image():
    result = MockProvider().analyse(SMALL_IMG)
    assert result.image_quality == "FAIL"
    assert result.recommended_action.value == "analysis_failed"
    assert result.observations == []


def test_inference_ms_is_positive():
    result = MockProvider().analyse(VALID_IMG)
    assert result.inference_ms >= 0


def test_health_reports_mock():
    h = MockProvider().health()
    assert h["provider"] == "mock"
    assert "note" in h


def test_deterministic_same_input_same_output():
    img = b"deterministic test" * 100
    r1 = MockProvider().analyse(img)
    r2 = MockProvider().analyse(img)
    assert r1.recommended_action == r2.recommended_action
    assert r1.image_quality == r2.image_quality
