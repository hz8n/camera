from collections import defaultdict, deque

import settings


class AlertStabilizer:
    """Requires repeated detector hits before an alert reaches logging/reporting."""

    def __init__(self):
        self.history = defaultdict(lambda: deque(maxlen=settings.ALERT_STABILITY_WINDOW))
        self.last_alert = {}

    def filter(self, alerts, stability_scale=1.0):
        current_types = {alert["type"] for alert in alerts}
        all_types = set(self.history.keys()) | current_types

        for event_type in all_types:
            self.history[event_type].append(event_type in current_types)

        stable_alerts = []
        for alert in alerts:
            event_type = alert["type"]
            min_hits = settings.ALERT_STABILITY_MIN_HITS.get(event_type, 3)
            min_hits = max(1, int(round(min_hits * stability_scale)))
            hits = sum(self.history[event_type])
            if hits >= min_hits:
                stable = dict(alert)
                stable["stability_hits"] = hits
                stable["stability_window"] = len(self.history[event_type])
                stable_alerts.append(stable)
        return stable_alerts
