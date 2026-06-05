from collections import Counter, deque
from datetime import datetime

import settings
from integrity_score import IntegrityScoreEngine


class SessionAnalyzer:
    """Maintains live session statistics and an interpretable risk score."""

    def __init__(self):
        self.started_at = None
        self.stopped_at = None
        self.frame_count = 0
        self.alert_count = 0
        self.alert_type_counts = Counter()
        self.severity_counts = Counter()
        self.category_counts = Counter()
        self.recent_risk = deque(maxlen=90)
        self.current_risk_score = 0
        self.max_risk_score = 0
        self.risk_timeline = []
        self.integrity_engine = IntegrityScoreEngine()

    def start(self):
        if self.started_at is None:
            self.started_at = datetime.now()
        self.stopped_at = None

    def stop(self):
        self.stopped_at = datetime.now()

    def update(self, alerts):
        self.frame_count += 1
        frame_score = 0
        for alert in alerts:
            event_type = alert["type"]
            frame_score += settings.RISK_WEIGHTS.get(event_type, 10)
            self.alert_type_counts[event_type] += 1
            self.severity_counts[alert.get("severity", "medium")] += 1
            self.category_counts[alert.get("category", "General")] += 1
            self.alert_count += 1

        frame_score = min(frame_score, 100)
        self.recent_risk.append(frame_score)
        self.current_risk_score = int(sum(self.recent_risk) / max(len(self.recent_risk), 1))
        self.max_risk_score = max(self.max_risk_score, self.current_risk_score)
        if self.frame_count % 15 == 0 or frame_score > 0:
            self.risk_timeline.append({
                "frame": self.frame_count,
                "score": self.current_risk_score,
                "instant_score": frame_score,
            })

    def get_summary(self, events=None):
        end_time = self.stopped_at or datetime.now()
        duration_seconds = 0
        if self.started_at:
            duration_seconds = int((end_time - self.started_at).total_seconds())
        integrity = self.integrity_engine.calculate(events or [])

        return {
            "started_at": self.started_at.isoformat(timespec="seconds") if self.started_at else None,
            "stopped_at": end_time.isoformat(timespec="seconds"),
            "duration_seconds": duration_seconds,
            "frame_count": self.frame_count,
            "alert_count": self.alert_count,
            "alert_type_counts": dict(self.alert_type_counts),
            "severity_counts": dict(self.severity_counts),
            "category_counts": dict(self.category_counts),
            "current_risk_score": self.current_risk_score,
            "max_risk_score": self.max_risk_score,
            "risk_label": self._risk_label(self.max_risk_score),
            "risk_timeline": self.risk_timeline[-200:],
            "integrity_score": integrity["integrity_score"],
            "integrity_label": integrity["integrity_label"],
            "integrity_deductions": integrity["deductions"],
        }

    def _risk_label(self, score):
        if score >= 70:
            return "High"
        if score >= 35:
            return "Medium"
        if score > 0:
            return "Low"
        return "Clear"
