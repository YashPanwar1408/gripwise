import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def analyze_tread(image_crop: np.ndarray) -> dict:
    """
    Estimate tread depth score proxy from tyre crop using Canny edges.
    IMPORTANT: This returns a relative proxy score, NOT a depth measurement in mm.
    """
    if image_crop is None or image_crop.size == 0:
        return {"tread_score": None, "groove_count": 0, "edge_density": 0.0}

    try:
        gray = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 45, 140)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

        h, w = edges.shape
        edge_density = float(np.count_nonzero(edges)) / float(h * w)
        
        # Approximate grooves
        strip_rows = np.linspace(int(h * 0.2), int(h * 0.8), num=8, dtype=int)
        counts = []
        for row in strip_rows:
            line = edges[row, :]
            transitions = np.diff(line.astype(np.int16))
            peaks = int(np.count_nonzero(np.abs(transitions) > 120))
            counts.append(peaks // 2)
        groove_count = int(np.median(counts)) if counts else 0

        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        contrast = float(np.std(gray))

        # Composite score
        groove_score = min(100.0, groove_count * 7.5)
        edge_score = min(100.0, edge_density * 420.0)
        texture_score = min(100.0, lap_var / 16.0)
        contrast_score = min(100.0, contrast * 2.4)

        tread_score = float(np.clip(
            0.32 * edge_score + 0.30 * groove_score + 0.23 * texture_score + 0.15 * contrast_score, 
            0.0, 100.0
        ))

        return {
            "tread_score": round(tread_score, 2),
            "groove_count": groove_count,
            "edge_density": round(edge_density, 5),
            "texture_variance": round(lap_var, 2)
        }
    except Exception as exc:
        logger.error(f"Tread analysis failed: {exc}")
        return {"tread_score": None, "groove_count": 0, "edge_density": 0.0}
