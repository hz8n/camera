import csv
import json
import os

import settings


class DataExporter:
    """Exports machine-readable session artifacts for grading and review."""

    def __init__(self, output_dir=settings.OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(self, events, session_summary, exam_profile, calibration_summary):
        csv_path = os.path.join(self.output_dir, "events.csv")
        session_path = os.path.join(self.output_dir, "session_summary.json")

        self._write_events_csv(csv_path, events)
        self._write_session_json(session_path, session_summary, exam_profile, calibration_summary)

        return {
            "events_csv": csv_path,
            "session_summary": session_path,
        }

    def _write_events_csv(self, path, events):
        columns = [
            "timestamp",
            "severity",
            "category",
            "type",
            "confidence",
            "risk_points",
            "message",
            "recommendation",
            "screenshot",
        ]
        with open(path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            for event in events:
                writer.writerow({column: event.get(column, "") for column in columns})

    def _write_session_json(self, path, session_summary, exam_profile, calibration_summary):
        payload = {
            "exam_profile": exam_profile,
            "session_summary": session_summary,
            "calibration": calibration_summary,
            "national_platform_demo": self._national_demo_metadata(),
            "privacy_note": "Local educational prototype. Manual review is required.",
        }
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def _national_demo_metadata(self):
        try:
            from national_platform_models import build_demo_national_topology

            return build_demo_national_topology()
        except Exception:
            return {}
