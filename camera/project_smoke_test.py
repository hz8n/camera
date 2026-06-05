import os
import tempfile

import cv2
import numpy as np

from alert_policy import AlertPolicy
from calibration import CalibrationManager
from dashboard_ui import DashboardUI
from data_exporter import DataExporter
from event_logger import EventLogger
from exam_profile import ExamProfile
from object_detector import ObjectDetector
from report_generator import ReportGenerator
from session_analyzer import SessionAnalyzer


def main():
    frame = np.full((720, 1280, 3), 90, dtype=np.uint8)
    output_dir = tempfile.mkdtemp(prefix="exam_monitor_smoke_")

    policy = AlertPolicy()
    alerts = policy.merge_frame_alerts([
        {"type": "student_absent", "message": "Smoke test absence", "severity": "high", "confidence": 0.9}
    ])

    logger = EventLogger(output_dir=output_dir, cooldown_seconds=0)
    logger.log_event(
        event_type=alerts[0]["type"],
        message=alerts[0]["message"],
        frame=frame,
        severity=alerts[0]["severity"],
        confidence=alerts[0]["confidence"],
        risk_points=alerts[0]["risk_points"],
        category=alerts[0]["category"],
        recommendation=alerts[0]["recommendation"],
        explanation=alerts[0]["explanation"],
    )
    events_path = logger.save()

    analyzer = SessionAnalyzer()
    analyzer.start()
    analyzer.update(alerts)
    analyzer.stop()
    summary = analyzer.get_summary(logger.events)

    calibration = CalibrationManager(required_frames=1)
    calibration_summary = {
        "calibrated": True,
        "samples": 1,
        "avg_brightness": 90,
        "avg_face_width": 100,
        "avg_face_height": 100,
    }

    profile = ExamProfile().to_dict()
    exports = DataExporter(output_dir=output_dir).export(logger.events, summary, profile, calibration_summary)
    report_path = ReportGenerator(output_dir=output_dir).generate(logger.events, summary, profile, calibration_summary, exports)

    detector_result = ObjectDetector().detect(frame)
    ui = DashboardUI("smoke")
    ui.draw(frame, {
        "alerts": alerts,
        "monitoring": True,
        "calibrating": False,
        "status": "MONITORING",
        "status_color": (95, 210, 135),
        "risk_score": summary["current_risk_score"],
        "max_risk_score": summary["max_risk_score"],
        "event_count": len(logger.events),
        "frame_count": summary["frame_count"],
        "calibration_progress": 100,
    })

    expected_paths = [events_path, exports["events_csv"], exports["session_summary"], report_path]
    missing = [path for path in expected_paths if not os.path.exists(path)]
    if missing:
        raise RuntimeError(f"Smoke test missing output files: {missing}")

    print("Smoke test passed.")
    print(f"Output directory: {output_dir}")
    print(f"Detector sample boxes: {len(detector_result['phone_boxes'])}")


if __name__ == "__main__":
    main()
