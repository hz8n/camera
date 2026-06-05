import argparse
import importlib.util
import os
import sys

import settings
from alert_policy import AlertPolicy
from alert_stabilizer import AlertStabilizer
from calibration import CalibrationManager
from camera_monitor import CameraMonitor
from control_center import ControlCenter
from dashboard_ui import DashboardUI
from data_exporter import DataExporter
from event_logger import EventLogger
from exam_profile import collect_exam_profile
from face_tracker import FaceTracker
from integrity_score import IntegrityScoreEngine
from national_platform_models import build_demo_national_topology
from object_detector import ObjectDetector
from report_generator import ReportGenerator
from session_analyzer import SessionAnalyzer


PROJECT_MODULES = [
    "settings",
    "camera_monitor",
    "control_center",
    "dashboard_ui",
    "face_tracker",
    "object_detector",
    "alert_policy",
    "alert_stabilizer",
    "calibration",
    "event_logger",
    "report_generator",
    "data_exporter",
    "session_analyzer",
    "exam_profile",
    "integrity_score",
    "national_platform_models",
]


OPTIONAL_PACKAGES = {
    "cv2": "OpenCV camera and image processing",
    "mediapipe": "Face mesh when the installed version supports it",
    "ultralytics": "YOLO object detection",
}


def main():
    """Project launcher that wires all modules before running the monitor."""
    args = _parse_args()
    _print_banner()
    _ensure_output_dirs()
    _print_system_status()
    _validate_project_modules()
    _preview_wiring()

    if args.check:
        print("Check complete. All project modules imported successfully.")
        return

    if args.no_run:
        print("No-run mode enabled. The monitor was not started.")
        return

    monitor = CameraMonitor(camera_index=args.camera)
    monitor.run()


def _parse_args():
    parser = argparse.ArgumentParser(description="National AI Exam Integrity Platform - local room node")
    parser.add_argument("--camera", type=int, default=settings.CAMERA_INDEX, help="Webcam index to open")
    parser.add_argument("--check", action="store_true", help="Only verify module wiring and dependencies")
    parser.add_argument("--no-run", action="store_true", help="Prepare and print wiring without opening camera")
    return parser.parse_args()


def _print_banner():
    print("=" * 72)
    print(settings.APP_TITLE)
    print("Local Room AI Node for the National AI Exam Integrity Platform")
    print("=" * 72)


def _ensure_output_dirs():
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.OUTPUT_DIR, settings.SCREENSHOT_DIR), exist_ok=True)


def _print_system_status():
    print("\nDependency Status")
    for package, purpose in OPTIONAL_PACKAGES.items():
        status = "OK" if importlib.util.find_spec(package) else "Missing"
        print(f"- {package:<12} {status:<8} {purpose}")
    print(f"- YOLO model   {'OK' if os.path.exists(settings.YOLO_MODEL) else 'Missing':<8} {settings.YOLO_MODEL}")


def _validate_project_modules():
    print("\nProject Module Wiring")
    for module_name in PROJECT_MODULES:
        if importlib.util.find_spec(module_name) is None:
            raise RuntimeError(f"Missing project module: {module_name}")
        print(f"- {module_name}: OK")


def _preview_wiring():
    print("\nRuntime Components")
    components = {
        "ControlCenter": ControlCenter,
        "DashboardUI": DashboardUI,
        "FaceTracker": FaceTracker,
        "ObjectDetector": ObjectDetector,
        "AlertPolicy": AlertPolicy,
        "AlertStabilizer": AlertStabilizer,
        "CalibrationManager": CalibrationManager,
        "EventLogger": EventLogger,
        "SessionAnalyzer": SessionAnalyzer,
        "IntegrityScoreEngine": IntegrityScoreEngine,
        "DataExporter": DataExporter,
        "ReportGenerator": ReportGenerator,
    }
    for name in components:
        print(f"- {name}: linked")

    topology = build_demo_national_topology()
    school_count = len(topology.get("schools", []))
    session_count = len(topology.get("active_sessions", []))
    print(f"- National demo topology: {school_count} school(s), {session_count} active session(s)")
    print("\nControls")
    print("- Mouse: Start, Stop, Calibrate, Report")
    print("- Keyboard: S, C, Q, P, M, F, O, T, 1, 2, 3, H, D")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(0)
