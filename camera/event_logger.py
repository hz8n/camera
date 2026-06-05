import json
import os
from datetime import datetime, timedelta

import cv2

import settings


class EventLogger:
    """Stores suspicious events and screenshot evidence."""

    def __init__(self, output_dir=settings.OUTPUT_DIR, cooldown_seconds=settings.EVENT_COOLDOWN_SECONDS):
        self.output_dir = output_dir
        self.screenshot_dir = os.path.join(output_dir, settings.SCREENSHOT_DIR)
        self.events_path = os.path.join(output_dir, "events.json")
        self.cooldown = timedelta(seconds=cooldown_seconds)
        self.events = []
        self.last_logged = {}

        os.makedirs(self.screenshot_dir, exist_ok=True)

    def should_log(self, event_type):
        now = datetime.now()
        last = self.last_logged.get(event_type)
        return last is None or now - last >= self.cooldown

    def log_event(
        self,
        event_type,
        message,
        frame,
        severity="medium",
        confidence=None,
        risk_points=0,
        category=None,
        recommendation=None,
        explanation=None,
    ):
        now = datetime.now()
        stamp = now.strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"{stamp}_{event_type}.jpg"
        screenshot_path = os.path.join(self.screenshot_dir, screenshot_name)
        cv2.imwrite(screenshot_path, frame)

        event = {
            "timestamp": now.isoformat(timespec="seconds"),
            "type": event_type,
            "severity": severity,
            "confidence": confidence,
            "risk_points": risk_points,
            "category": category,
            "recommendation": recommendation,
            "explanation": explanation,
            "message": message,
            "screenshot": screenshot_path,
        }
        self.events.append(event)
        self.last_logged[event_type] = now
        print(f"[ALERT] {event['timestamp']} - {message}")
        return event

    def save(self):
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.events_path, "w", encoding="utf-8") as file:
            json.dump(self.events, file, indent=2)
        return self.events_path
