from collections import deque

import cv2
import mediapipe as mp

import settings


class FaceTracker:
    """Detects people, absence, and repeated looking-away behavior."""

    def __init__(self):
        self.backend = "opencv"
        self.face_detection = None
        self.face_mesh = None
        self.face_cascade = None
        self.profile_cascade = None
        self.eye_cascade = None
        self.reference_face_center = None
        self._setup_backend()
        self.look_away_history = deque(maxlen=settings.LOOK_AWAY_WINDOW_FRAMES)
        self.absence_history = deque(maxlen=settings.ABSENCE_GRACE_FRAMES)
        self.multi_person_history = deque(maxlen=settings.MULTIPLE_PEOPLE_GRACE_FRAMES)

    def _setup_backend(self):
        if hasattr(mp, "solutions"):
            self.backend = "mediapipe"
            mp_face_detection = mp.solutions.face_detection
            mp_face_mesh = mp.solutions.face_mesh
            self.face_detection = mp_face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=settings.FACE_DETECTION_CONFIDENCE,
            )
            self.face_mesh = mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=settings.FACE_DETECTION_CONFIDENCE,
                min_tracking_confidence=settings.FACE_TRACKING_CONFIDENCE,
            )
            return

        frontal_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        profile_path = cv2.data.haarcascades + "haarcascade_profileface.xml"
        eye_path = cv2.data.haarcascades + "haarcascade_eye.xml"
        self.face_cascade = cv2.CascadeClassifier(frontal_path)
        self.profile_cascade = cv2.CascadeClassifier(profile_path)
        self.eye_cascade = cv2.CascadeClassifier(eye_path)
        if self.face_cascade.empty():
            raise RuntimeError("OpenCV face cascade could not be loaded.")
        print("MediaPipe Solutions API was not found. Using OpenCV face detection fallback.")

    def analyze(self, frame):
        h, w = frame.shape[:2]
        faces, mesh_result = self._detect_faces(frame, w, h)

        alerts = []
        no_face = len(faces) == 0
        multiple_faces = len(faces) > 1
        self.absence_history.append(no_face)
        self.multi_person_history.append(multiple_faces)

        if len(self.absence_history) == self.absence_history.maxlen and all(self.absence_history):
            alerts.append({
                "type": "student_absent",
                "message": "Student left camera view for several frames",
                "severity": "high",
                "confidence": 0.9,
            })
        elif len(self.multi_person_history) == self.multi_person_history.maxlen and any(self.multi_person_history):
            alerts.append({
                "type": "multiple_people",
                "message": f"More than one person detected ({len(faces)} faces)",
                "severity": "high",
                "confidence": 0.85,
            })

        looking_away = self._is_looking_away(mesh_result, faces, w, h)
        self.look_away_history.append(looking_away)
        look_away_count = sum(self.look_away_history)
        if look_away_count >= settings.LOOK_AWAY_ALERT_THRESHOLD:
            alerts.append({
                "type": "frequent_look_away",
                "message": f"Student looked away too often ({look_away_count}/{len(self.look_away_history)} frames)",
                "severity": "medium",
                "confidence": round(look_away_count / max(len(self.look_away_history), 1), 2),
            })

        brightness = cv2.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))[0]
        if brightness < 35:
            alerts.append({
                "type": "low_visibility",
                "message": "Camera image is too dark for reliable monitoring",
                "severity": "low",
                "confidence": 0.65,
            })

        return {
            "faces": faces,
            "looking_away": looking_away,
            "face_count": len(faces),
            "brightness": round(brightness, 1),
            "backend": self.backend,
            "alerts": alerts,
        }

    def _detect_faces(self, frame, width, height):
        if self.backend == "mediapipe":
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detection_result = self.face_detection.process(rgb)
            mesh_result = self.face_mesh.process(rgb)

            faces = []
            if detection_result.detections:
                for detection in detection_result.detections:
                    box = detection.location_data.relative_bounding_box
                    x1 = max(0, int(box.xmin * width))
                    y1 = max(0, int(box.ymin * height))
                    x2 = min(width, int((box.xmin + box.width) * width))
                    y2 = min(height, int((box.ymin + box.height) * height))
                    faces.append((x1, y1, x2, y2))
            return faces, mesh_result

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frontal = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.12,
            minNeighbors=5,
            minSize=(60, 60),
        )
        profiles = []
        if self.profile_cascade is not None and not self.profile_cascade.empty():
            profiles = self.profile_cascade.detectMultiScale(
                gray,
                scaleFactor=1.12,
                minNeighbors=5,
                minSize=(60, 60),
            )

        faces = [(int(x), int(y), int(x + fw), int(y + fh)) for x, y, fw, fh in frontal]
        profile_faces = [(int(x), int(y), int(x + fw), int(y + fh)) for x, y, fw, fh in profiles]
        faces = self._merge_boxes(faces + profile_faces)
        return faces, None

    def _merge_boxes(self, boxes):
        merged = []
        for box in sorted(boxes, key=lambda item: (item[0], item[1])):
            if not any(self._iou(box, existing) > 0.35 for existing in merged):
                merged.append(box)
        return merged

    def _iou(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
        area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
        area_b = max(1, (bx2 - bx1) * (by2 - by1))
        return inter / float(area_a + area_b - inter)

    def _is_looking_away(self, mesh_result, faces, width, height):
        if self.backend == "opencv":
            return self._opencv_look_away_estimate(faces, width, height)

        if not mesh_result.multi_face_landmarks:
            return False

        landmarks = mesh_result.multi_face_landmarks[0].landmark
        nose = landmarks[1]
        left_cheek = landmarks[234]
        right_cheek = landmarks[454]
        chin = landmarks[152]
        forehead = landmarks[10]

        face_center_x = (left_cheek.x + right_cheek.x) / 2
        face_width = max(abs(right_cheek.x - left_cheek.x), 0.001)
        horizontal_offset = abs(nose.x - face_center_x) / face_width

        face_center_y = (forehead.y + chin.y) / 2
        face_height = max(abs(chin.y - forehead.y), 0.001)
        vertical_offset = abs(nose.y - face_center_y) / face_height

        return (
            horizontal_offset > settings.LOOK_AWAY_HORIZONTAL_RATIO
            or vertical_offset > settings.LOOK_AWAY_VERTICAL_RATIO
        )

    def _opencv_look_away_estimate(self, faces, width, height):
        if len(faces) != 1:
            return False

        x1, y1, x2, y2 = faces[0]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        face_w = max(x2 - x1, 1)
        face_h = max(y2 - y1, 1)

        if self.reference_face_center is None:
            self.reference_face_center = (center_x, center_y)
            return False

        ref_x, ref_y = self.reference_face_center
        self.reference_face_center = (
            ref_x * 0.98 + center_x * 0.02,
            ref_y * 0.98 + center_y * 0.02,
        )

        horizontal_shift = abs(center_x - ref_x) / face_w
        vertical_shift = abs(center_y - ref_y) / face_h
        near_edge = center_x < width * 0.2 or center_x > width * 0.8
        return horizontal_shift > 0.45 or vertical_shift > 0.35 or near_edge

    def draw(self, frame, result):
        for x1, y1, x2, y2 in result["faces"]:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (40, 220, 40), 2)

        if result["looking_away"]:
            cv2.putText(frame, "Looking away", (16, frame.shape[0] - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 255), 2)

        cv2.putText(
            frame,
            f"Faces: {result['face_count']}  Brightness: {result['brightness']}",
            (16, frame.shape[0] - 54),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (230, 230, 230),
            1,
        )
        cv2.putText(
            frame,
            f"Face backend: {result['backend']}",
            (260, frame.shape[0] - 54),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (230, 230, 230),
            1,
        )

        return frame
