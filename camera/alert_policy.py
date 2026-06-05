import settings


SEVERITY_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


class AlertPolicy:
    """Converts raw detector alerts into richer university-style incidents."""

    def enrich(self, alert):
        event_type = alert["type"]
        risk_points = settings.RISK_WEIGHTS.get(event_type, 10)
        confidence = alert.get("confidence")
        severity = alert.get("severity", self._severity_from_risk(risk_points))

        enriched = dict(alert)
        enriched["severity"] = severity
        enriched["risk_points"] = risk_points
        enriched["confidence"] = confidence
        enriched["category"] = self._category(event_type)
        enriched["recommendation"] = self._recommendation(event_type)
        enriched["explanation"] = self._explanation(event_type)
        return enriched

    def merge_frame_alerts(self, alerts):
        enriched = [self.enrich(alert) for alert in alerts]
        enriched.sort(
            key=lambda item: (
                SEVERITY_ORDER.get(item.get("severity", "low"), 0),
                item.get("risk_points", 0),
            ),
            reverse=True,
        )
        return enriched

    def _severity_from_risk(self, risk_points):
        if risk_points >= 40:
            return "high"
        if risk_points >= 20:
            return "medium"
        return "low"

    def _category(self, event_type):
        categories = {
            "student_absent": "Presence",
            "multiple_people": "Environment",
            "frequent_look_away": "Attention",
            "phone_like_object": "Object",
            "low_visibility": "Camera Quality",
            "ai_person_count": "Environment",
            "ai_cell_phone": "Object",
            "manual_snapshot": "Manual Review",
        }
        return categories.get(event_type, "General")

    def _recommendation(self, event_type):
        recommendations = {
            "student_absent": "Review screenshot evidence and confirm whether the student left the exam area.",
            "multiple_people": "Review whether another person was visible near the student.",
            "frequent_look_away": "Check whether the student was reading allowed material or repeatedly looking off-screen.",
            "phone_like_object": "Review the image manually because rectangular objects can create false positives.",
            "low_visibility": "Improve lighting or camera angle before relying on detection results.",
            "ai_person_count": "Review the AI-detected person boxes and confirm whether another person was present.",
            "ai_cell_phone": "Review evidence immediately because an AI object model detected a phone-like device.",
            "manual_snapshot": "Review manually captured context.",
        }
        return recommendations.get(event_type, "Review the screenshot and session context.")

    def _explanation(self, event_type):
        explanations = {
            "student_absent": "The system did not detect a face for multiple consecutive frames.",
            "multiple_people": "The face detector found more than one face in the webcam frame.",
            "frequent_look_away": "The student appeared to look away repeatedly inside a sliding time window.",
            "phone_like_object": "OpenCV found a rectangular object with phone-like proportions.",
            "low_visibility": "The average brightness was below the configured reliability threshold.",
            "ai_person_count": "The optional YOLO object detector found more than one person.",
            "ai_cell_phone": "The optional YOLO object detector identified a phone-like class.",
            "manual_snapshot": "A supervisor manually captured this frame.",
        }
        return explanations.get(event_type, "The detector produced a suspicious behavior signal.")
