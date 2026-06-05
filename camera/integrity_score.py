class IntegrityScoreEngine:
    """Calculates a student integrity score from monitoring evidence.

    The score starts at 100 and decreases based on confirmed suspicious signals.
    This is explainable and suitable for a prototype report; it is not a final
    legal decision system.
    """

    PENALTIES = {
        "student_absent": 18,
        "multiple_people": 22,
        "frequent_look_away": 10,
        "phone_like_object": 24,
        "ai_person_count": 24,
        "ai_cell_phone": 35,
        "low_visibility": 6,
        "rf_device_signal": 28,
        "bluetooth_device_signal": 20,
        "wifi_device_signal": 18,
        "identity_mismatch": 40,
        "voice_mismatch": 28,
        "collaboration_pattern": 30,
        "answer_similarity": 25,
    }

    def calculate(self, events):
        score = 100
        reasons = []

        for event in events:
            event_type = event.get("type", "unknown")
            confidence = event.get("confidence")
            confidence = confidence if isinstance(confidence, (int, float)) else 0.75
            penalty = self.PENALTIES.get(event_type, 8)
            weighted_penalty = int(round(penalty * max(0.35, min(confidence, 1.0))))
            score -= weighted_penalty
            reasons.append({
                "event_type": event_type,
                "penalty": weighted_penalty,
                "confidence": confidence,
                "message": event.get("message", ""),
            })

        score = max(0, min(100, score))
        return {
            "integrity_score": score,
            "integrity_label": self._label(score),
            "deductions": reasons,
        }

    def _label(self, score):
        if score >= 85:
            return "Trusted"
        if score >= 65:
            return "Needs Review"
        if score >= 40:
            return "High Concern"
        return "Critical Review"

