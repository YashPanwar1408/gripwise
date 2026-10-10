import cv2
import numpy as np

def detect_anomalies(image_crop: np.ndarray) -> dict:
    """
    Detects potential anomalies (e.g. uneven wear, cracks) using geometric checks.
    Returns anomaly severity proxy score 0-100 and a boolean flag based on high thresholds.
    """
    if image_crop is None or image_crop.size == 0:
        return {"anomaly_score": 0.0, "anomaly_detected": False}

    try:
        gray = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding to find deep cuts/cracks
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological noise removal
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        anomaly_score = 0.0
        anomalous_regions = 0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filter small noise
            if 50 < area < (gray.shape[0] * gray.shape[1] * 0.1):
                # Calculate circularity/shape metrics
                perimeter = cv2.arcLength(cnt, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * (area / (perimeter * perimeter))
                    if circularity < 0.3: # Elongated shapes (potential cracks)
                        anomalous_regions += 1
                        anomaly_score += min(10.0, area / 100.0)

        anomaly_score = min(100.0, anomaly_score)
        anomaly_detected = anomaly_score > 35.0

        return {
            "anomaly_score": round(anomaly_score, 2),
            "anomaly_detected": anomaly_detected,
            "anomalous_regions": anomalous_regions
        }
    except Exception:
        return {"anomaly_score": 0.0, "anomaly_detected": False}
