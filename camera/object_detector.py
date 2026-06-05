import cv2

import settings


class ObjectDetector:
    """Detects phones and extra people using optional YOLO plus OpenCV fallback."""

    def __init__(self):
        self.min_area = settings.PHONE_MIN_AREA
        self.max_area = settings.PHONE_MAX_AREA
        self.frame_index = 0
        self.yolo_model = None
        self.yolo_available = False
        self.last_ai_result = {"phone_boxes": [], "person_boxes": [], "alerts": []}
        self._setup_yolo()

    def _setup_yolo(self):
        if not settings.ENABLE_YOLO_OBJECT_DETECTION:
            return
        try:
            from ultralytics import YOLO

            self.yolo_model = YOLO(settings.YOLO_MODEL)
            self.yolo_available = True
            print(f"YOLO object detection enabled: {settings.YOLO_MODEL}")
        except Exception as exc:
            print(f"YOLO unavailable, using OpenCV shape fallback only: {exc}")

    def detect(self, frame):
        self.frame_index += 1
        if self.yolo_available and self.frame_index % settings.YOLO_PROCESS_EVERY_N_FRAMES == 0:
            self.last_ai_result = self._detect_with_yolo(frame)

        fallback = self._detect_phone_shapes(frame)
        phone_boxes = self.last_ai_result["phone_boxes"] + fallback["phone_boxes"]
        person_boxes = self.last_ai_result["person_boxes"]
        alerts = self.last_ai_result["alerts"] + fallback["alerts"]

        return {
            "phone_boxes": phone_boxes,
            "person_boxes": person_boxes,
            "alerts": alerts,
            "backend": "yolo+opencv" if self.yolo_available else "opencv-shape",
        }

    def _detect_with_yolo(self, frame):
        results = self.yolo_model.predict(frame, conf=settings.YOLO_CONFIDENCE, verbose=False)
        phone_boxes = []
        person_boxes = []
        alerts = []

        if not results:
            return {"phone_boxes": [], "person_boxes": [], "alerts": []}

        names = results[0].names
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            label = names[class_id]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = [int(value) for value in box.xyxy[0]]

            if label == "person":
                person_boxes.append({"box": (x1, y1, x2, y2), "confidence": round(confidence, 2), "source": "yolo"})
            elif label in ("cell phone", "laptop", "remote"):
                phone_boxes.append({"box": (x1, y1, x2, y2), "confidence": round(confidence, 2), "source": f"yolo:{label}"})

        if len(person_boxes) > 1:
            alerts.append({
                "type": "ai_person_count",
                "message": f"AI model detected {len(person_boxes)} people",
                "severity": "high",
                "confidence": max(item["confidence"] for item in person_boxes),
            })
        if phone_boxes:
            best = max(phone_boxes, key=lambda item: item["confidence"])
            alerts.append({
                "type": "ai_cell_phone",
                "message": f"AI model detected phone-like device ({best['source']}, confidence {best['confidence']})",
                "severity": "critical",
                "confidence": best["confidence"],
            })

        return {"phone_boxes": phone_boxes, "person_boxes": person_boxes, "alerts": alerts}

    def _detect_phone_shapes(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 60, 160)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        phone_boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area or area > self.max_area:
                continue

            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.035 * perimeter, True)
            if len(approx) != 4:
                continue

            x, y, w, h = cv2.boundingRect(approx)
            if w == 0 or h == 0:
                continue

            aspect = max(w, h) / min(w, h)
            rectangular_fill = area / float(w * h)
            if settings.PHONE_MIN_ASPECT <= aspect <= settings.PHONE_MAX_ASPECT and rectangular_fill > settings.PHONE_MIN_FILL_RATIO:
                confidence = min(0.95, 0.5 + rectangular_fill / 2)
                phone_boxes.append({
                    "box": (x, y, x + w, y + h),
                    "confidence": round(confidence, 2),
                    "area": int(area),
                    "aspect_ratio": round(aspect, 2),
                    "source": "opencv-shape",
                })

        alerts = []
        if phone_boxes:
            best = max(phone_boxes, key=lambda item: item["confidence"])
            alerts.append({
                "type": "phone_like_object",
                "message": f"Phone-like object detected (confidence {best['confidence']})",
                "severity": "high",
                "confidence": best["confidence"],
            })

        return {"phone_boxes": phone_boxes, "alerts": alerts}

    def draw(self, frame, result):
        for item in result["phone_boxes"]:
            x1, y1, x2, y2 = item["box"]
            color = (80, 80, 255) if str(item.get("source", "")).startswith("yolo") else (255, 80, 80)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{item.get('source', 'phone')} {item['confidence']}", (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        for item in result.get("person_boxes", []):
            x1, y1, x2, y2 = item["box"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 210, 255), 2)
            cv2.putText(frame, f"person {item['confidence']}", (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 210, 255), 2)
        return frame
