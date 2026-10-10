import time
import cv2
import numpy as np

from ai.interfaces import (
    InferenceProvider, InferenceResult, TyreObservation, 
    ConfidenceTier, RecommendedAction
)
from ai.tyre_pipeline.quality_checker import check_image_quality
from ai.tyre_pipeline.detector import detect_tyres
from ai.tyre_pipeline.tread_analyser import analyze_tread
from ai.tyre_pipeline.anomaly_detector import detect_anomalies

VERSION = "cv-pipeline-1.0.0"

class CVProvider:
    def analyse(self, image_bytes: bytes) -> InferenceResult:
        start_t = time.perf_counter()
        
        # 1. Decode image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return self._fail_result(start_t, ["CORRUPT_IMAGE"])

        # 2. Quality Check
        q_status, q_issues = check_image_quality(img)
        if q_status == "FAIL":
            return self._fail_result(start_t, q_issues)

        # 3. Detect Tyres
        detections = detect_tyres(img)
        if not detections:
            return self._not_found_result(start_t, q_status, q_issues)
        
        # Take the largest confident bounding box
        main_tyre = detections[0]
        x1, y1, x2, y2 = main_tyre["bbox"]
        tyre_crop = img[y1:y2, x1:x2]

        # 4. Tread Analysis
        tread_res = analyze_tread(tyre_crop)
        tread_score = tread_res["tread_score"]

        # 5. Anomaly Detection
        anomaly_res = detect_anomalies(tyre_crop)
        anomaly_detected = anomaly_res["anomaly_detected"]

        # 6. Confidence Tier Derivation
        # Rule: tread_score -> HIGH if PASS & detected_tyres >= 1
        tread_conf = ConfidenceTier.LOW
        if tread_score is not None:
            if q_status == "PASS" and main_tyre["method"] == "yolo":
                tread_conf = ConfidenceTier.HIGH
            elif q_status == "DEGRADED" or main_tyre["method"] != "yolo":
                tread_conf = ConfidenceTier.MEDIUM

        anomaly_conf = ConfidenceTier.LOW
        if q_status == "PASS" and main_tyre["method"] == "yolo":
            anomaly_conf = ConfidenceTier.HIGH
        elif q_status == "DEGRADED":
            anomaly_conf = ConfidenceTier.MEDIUM

        # 7. Action Recommendation
        if tread_score is None:
            action = RecommendedAction.ANALYSIS_FAILED
            expl = "Could not compute tread proxy."
        elif tread_score < 30 or anomaly_detected:
            action = RecommendedAction.INSPECT_SOON
            expl = "Tread proxy is low or anomalies detected. Schedule physical inspection."
        elif tread_score < 50:
            action = RecommendedAction.MONITOR
            expl = "Tread proxy indicates moderate wear. Monitor closely."
        else:
            action = RecommendedAction.OK
            expl = "Tread indicator is healthy. No action required."

        observations = []
        if tread_score is not None:
            observations.append(TyreObservation(
                field="tread_score_proxy",
                value=tread_score,
                confidence=tread_conf,
                explanation="Relative proxy for tread wear (0-100), not an absolute measurement.",
                caveat="This is an AI estimation based on image texture and edges. Always rely on a physical tread depth gauge."
            ))

        observations.append(TyreObservation(
            field="anomaly_detected",
            value=anomaly_detected,
            confidence=anomaly_conf,
            explanation="Indicates geometric irregularities such as uneven wear or cracks.",
            caveat="High false-positive rate on dirty tyres. Not a confirmed puncture."
        ))

        return InferenceResult(
            provider="cv_pipeline",
            model_version=VERSION,
            image_quality=q_status,
            quality_issues=q_issues,
            detected_tyres=len(detections),
            recommended_action=action,
            recommended_action_explanation=expl,
            observations=observations,
            raw_scores={**tread_res, **anomaly_res, "detection_method": main_tyre["method"]},
            inference_ms=(time.perf_counter() - start_t) * 1000.0
        )

    def health(self) -> dict:
        try:
            import ultralytics
            yolo_ok = True
        except ImportError:
            yolo_ok = False
            
        return {
            "provider": "cv_pipeline",
            "version": VERSION,
            "status": "healthy",
            "yolo_available": yolo_ok,
            "opencv_available": True,
            "condition_classifier_available": False # Removed in Phase 2
        }

    def _fail_result(self, start_t: float, issues: list[str]) -> InferenceResult:
        return InferenceResult(
            provider="cv_pipeline", model_version=VERSION,
            image_quality="FAIL", quality_issues=issues,
            detected_tyres=0,
            recommended_action=RecommendedAction.ANALYSIS_FAILED,
            recommended_action_explanation="Image quality is too low for analysis.",
            observations=[], raw_scores={},
            inference_ms=(time.perf_counter() - start_t) * 1000.0
        )

    def _not_found_result(self, start_t: float, q_status: str, issues: list[str]) -> InferenceResult:
        return InferenceResult(
            provider="cv_pipeline", model_version=VERSION,
            image_quality=q_status, quality_issues=issues,
            detected_tyres=0,
            recommended_action=RecommendedAction.SEEK_MECHANIC_NOW,
            recommended_action_explanation="No tyre detected confidently in image. Physical inspection recommended.",
            observations=[TyreObservation(
                field="tread_score_proxy", value=None, confidence=ConfidenceTier.NOT_AVAILABLE,
                explanation="Tyre not detected in image.", caveat="Upload a clearer image or consult a mechanic."
            )], raw_scores={},
            inference_ms=(time.perf_counter() - start_t) * 1000.0
        )
