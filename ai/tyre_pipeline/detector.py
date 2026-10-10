import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

ALLOW_PRETRAINED = os.getenv("GRIPWISE_ALLOW_PRETRAINED_YOLO", "0") in ("1", "true")

def detect_tyres(image: np.ndarray) -> list[dict]:
    """
    Detect tyre regions. 
    Attempts YOLO if available, otherwise falls back to OpenCV Hough circles.
    Returns a list of dicts: {"bbox": [x1, y1, x2, y2], "confidence": float, "label": "tyre", "method": str}
    """
    if image is None or image.size == 0:
        return []

    # In MVP Phase 2 without real weights, we mostly rely on Hough fallback 
    # unless ALLOW_PRETRAINED is explicitly enabled.
    if ALLOW_PRETRAINED:
        try:
            from ultralytics import YOLO
            model = YOLO("yolov8n.pt") # lightweight fallback
            results = model.predict(image, conf=0.25, verbose=False)
            
            detections = []
            for result in results:
                if result.boxes is None:
                    continue
                names = getattr(result, "names", {})
                for i in range(len(result.boxes)):
                    cls_id = int(result.boxes.cls[i].item())
                    conf = float(result.boxes.conf[i].item())
                    x1, y1, x2, y2 = [int(v) for v in result.boxes.xyxy[i].tolist()]
                    cls_name = str(names.get(cls_id, "")).lower()
                    
                    if "tyre" in cls_name or "tire" in cls_name or "wheel" in cls_name:
                        detections.append({"bbox": [x1, y1, x2, y2], "confidence": conf, "label": "tyre", "method": "yolo"})
                        continue
                    
                    # Vehicle proxy fallback
                    if cls_id in {2, 3, 5, 7}:  # car, motorcycle, bus, truck
                        h = max(1, y2 - y1)
                        w = max(1, x2 - x1)
                        tyre_h = int(h * 0.30)
                        tyre_w = int(w * 0.25)
                        detections.append({
                            "bbox": [x1, max(y1, y2 - tyre_h), min(x2, x1 + tyre_w), y2],
                            "confidence": conf * 0.5,
                            "label": "tyre_proxy",
                            "method": "yolo_vehicle_crop"
                        })
                        
            if detections:
                return detections
        except ImportError:
            logger.warning("ultralytics not installed. Falling back to OpenCV detection.")
        except Exception as exc:
            logger.warning(f"YOLO inference failed: {exc}. Falling back to OpenCV detection.")

    return _detect_opencv_fallback(image)


def _detect_opencv_fallback(image: np.ndarray) -> list[dict]:
    """Hough circle fallback for tyre detection."""
    detections = []
    orig_h, orig_w = image.shape[:2]
    max_dim = max(orig_h, orig_w)
    scale = 1.0 if max_dim <= 960 else 960.0 / max_dim

    work_img = image if scale == 1.0 else cv2.resize(image, (int(orig_w * scale), int(orig_h * scale)))
    gray = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)
    h, w = gray.shape[:2]

    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=max(30, min(h, w) // 4),
        param1=120, param2=38, minRadius=max(15, min(h, w) // 10), maxRadius=max(20, min(h, w) // 2)
    )

    if circles is not None:
        for circle in np.round(circles[0]).astype(int):
            cx, cy, radius = circle.tolist()
            x1, y1 = max(0, cx - radius), max(0, cy - radius)
            x2, y2 = min(w, cx + radius), min(h, cy + radius)

            if scale != 1.0:
                x1, y1, x2, y2 = int(x1 / scale), int(y1 / scale), int(x2 / scale), int(y2 / scale)

            x1 = max(0, min(x1, orig_w - 1))
            y1 = max(0, min(y1, orig_h - 1))
            x2 = max(x1 + 1, min(x2, orig_w))
            y2 = max(y1 + 1, min(y2, orig_h))
            
            # Use low confidence for Hough
            detections.append({"bbox": [x1, y1, x2, y2], "confidence": 0.4, "label": "tyre", "method": "hough_circle"})

    return sorted(detections, key=lambda d: (d["bbox"][2]-d["bbox"][0])*(d["bbox"][3]-d["bbox"][1]), reverse=True)[:3]
