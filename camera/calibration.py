import cv2


class CalibrationManager:
    """Measures baseline brightness and face position before monitoring starts."""

    def __init__(self, required_frames=45):
        self.required_frames = required_frames
        self.samples = []
        self.completed = False
        self.summary = {}

    def reset(self):
        self.samples = []
        self.completed = False
        self.summary = {}

    def update(self, frame, face_result):
        if self.completed:
            return self.summary

        faces = face_result.get("faces", [])
        if len(faces) == 1:
            x1, y1, x2, y2 = faces[0]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = cv2.mean(gray)[0]
            self.samples.append({
                "brightness": brightness,
                "face_center_x": (x1 + x2) / 2,
                "face_center_y": (y1 + y2) / 2,
                "face_width": x2 - x1,
                "face_height": y2 - y1,
            })

        if len(self.samples) >= self.required_frames:
            self.completed = True
            self.summary = self._build_summary()
        return self.summary

    def progress(self):
        return min(100, int((len(self.samples) / self.required_frames) * 100))

    def _build_summary(self):
        count = len(self.samples)
        return {
            "calibrated": True,
            "samples": count,
            "avg_brightness": round(sum(item["brightness"] for item in self.samples) / count, 2),
            "avg_face_width": round(sum(item["face_width"] for item in self.samples) / count, 2),
            "avg_face_height": round(sum(item["face_height"] for item in self.samples) / count, 2),
        }

