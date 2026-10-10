import cv2
import numpy as np

def check_image_quality(image: np.ndarray) -> tuple[str, list[str]]:
    """
    Evaluates image for blur, brightness, and resolution.
    Returns: status (PASS/DEGRADED/FAIL), and a list of issues.
    """
    if image is None or image.size == 0:
        return "FAIL", ["EMPTY_IMAGE"]

    issues = []
    h, w = image.shape[:2]
    
    # Check resolution
    if w < 224 or h < 224:
        issues.append("LOW_RESOLUTION")
    if w < 100 or h < 100:
        return "FAIL", ["RESOLUTION_TOO_LOW"]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Check brightness
    mean_brightness = np.mean(gray)
    if mean_brightness < 40:
        issues.append("TOO_DARK")
    elif mean_brightness > 220:
        issues.append("TOO_BRIGHT")

    # Check blur (Laplacian variance)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if lap_var < 50.0:
        issues.append("BLURRED")
        if lap_var < 15.0:
            return "FAIL", issues

    if len(issues) > 0:
        return "DEGRADED", issues
        
    return "PASS", []
