from datetime import datetime

import cv2

import settings
from alert_policy import AlertPolicy
from alert_stabilizer import AlertStabilizer
from calibration import CalibrationManager
from control_center import ControlCenter
from dashboard_ui import DashboardUI
from data_exporter import DataExporter
from event_logger import EventLogger
from exam_profile import collect_exam_profile
from face_tracker import FaceTracker
from object_detector import ObjectDetector
from report_generator import ReportGenerator
from session_analyzer import SessionAnalyzer


class CameraMonitor:
    """Coordinates camera input, detectors, logging, dashboard, and reports."""

    def __init__(self, camera_index=settings.CAMERA_INDEX):
        self.window_name = settings.WINDOW_NAME
        self.camera_index = camera_index
        self.face_tracker = FaceTracker()
        self.object_detector = ObjectDetector()
        self.alert_policy = AlertPolicy()
        self.alert_stabilizer = AlertStabilizer()
        self.calibration_manager = CalibrationManager()
        self.session_analyzer = SessionAnalyzer()
        self.event_logger = EventLogger()
        self.report_generator = ReportGenerator()
        self.data_exporter = DataExporter()
        self.dashboard = DashboardUI(self.window_name)
        self.controls = ControlCenter()
        self.exam_profile = None
        self.monitoring = False
        self.calibrating = False
        self.quit_requested = False
        self._manual_snapshot_pending = False
        self.last_alerts = []

    def run(self):
        self._print_startup_message()
        self.exam_profile = collect_exam_profile()

        cap = self._open_camera()
        if cap is None:
            return

        self.dashboard.attach()
        while not self.quit_requested:
            ok, frame = cap.read()
            if not ok:
                print("Could not read frame from webcam.")
                break

            frame = cv2.flip(frame, 1)
            self._apply_control_requests()
            alerts = self._process_frame(frame)
            self._draw_frame(frame, alerts)
            cv2.imshow(self.window_name, frame)
            self._handle_inputs()

        cap.release()
        cv2.destroyAllWindows()
        self._finish_session()

    def _open_camera(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("Could not open webcam. Check camera permissions or CAMERA_INDEX in settings.py.")
            return None
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.FRAME_HEIGHT)
        return cap

    def _process_frame(self, frame):
        alerts = []
        if self.calibrating:
            face_result = self.face_tracker.analyze(frame)
            self.calibration_manager.update(frame, face_result)
            self.face_tracker.draw(frame, face_result)
            if self.calibration_manager.completed:
                self.calibrating = False
                self.monitoring = True
                self.session_analyzer.start()
                print("Calibration complete. Monitoring started.")
            return alerts

        if not self.monitoring:
            self._save_manual_snapshot_if_requested(frame)
            return alerts

        face_result = {"alerts": []}
        object_result = {"alerts": [], "phone_boxes": [], "person_boxes": []}
        if self.controls.state.enable_face_detection:
            face_result = self.face_tracker.analyze(frame)
        if self.controls.state.enable_object_detection:
            object_result = self.object_detector.detect(frame)
        raw_alerts = face_result["alerts"] + object_result["alerts"]
        enriched_alerts = self.alert_policy.merge_frame_alerts(raw_alerts)
        profile = self.controls.active_profile()
        alerts = (
            self.alert_stabilizer.filter(enriched_alerts, profile["stability_scale"])
            if self.controls.state.enable_stabilizer
            else enriched_alerts
        )
        alerts = self._apply_runtime_sensitivity(alerts, profile["risk_multiplier"])

        self.session_analyzer.update(alerts)
        self._record_alerts(alerts, frame)
        self._save_manual_snapshot_if_requested(frame)
        if self.controls.state.enable_face_detection:
            self.face_tracker.draw(frame, face_result)
        if self.controls.state.enable_object_detection:
            self.object_detector.draw(frame, object_result)
        return alerts

    def _draw_frame(self, frame, alerts):
        visible_alerts = alerts if alerts else self.last_alerts
        self.dashboard.draw(frame, {
            "alerts": visible_alerts,
            "monitoring": self.monitoring,
            "calibrating": self.calibrating,
            "status": self._status_text(),
            "status_color": self._status_color(),
            "risk_score": self.session_analyzer.current_risk_score,
            "max_risk_score": self.session_analyzer.max_risk_score,
            "event_count": len(self.event_logger.events),
            "frame_count": self.session_analyzer.frame_count,
            "calibration_progress": self.calibration_manager.progress(),
            "sensitivity_mode": self.controls.active_profile()["name"],
            "control_cards": self.controls.status_cards(),
            "show_help": self.controls.state.show_help,
            "show_debug": self.controls.state.show_debug,
            "help_lines": self.controls.help_lines(),
            "command_log": self.controls.state.command_log,
            "alerts_muted": self.controls.state.alerts_muted,
        })

    def _handle_inputs(self):
        action = self.dashboard.pop_action()
        key = cv2.waitKey(1) & 0xFF

        if action:
            mapped = "toggle_monitoring" if action == "start" else action
            self.controls.handle_action(mapped)
        if key != 255:
            self.controls.handle_key(key)

    def _apply_control_requests(self):
        if self.controls.consume_report_request():
            self.quit_requested = True
            return
        if self.controls.consume_snapshot_request():
            self._manual_snapshot_pending = True
        if self.controls.consume_calibration_request():
            self._start_calibration()
        if not self.controls.state.monitoring_enabled and self.monitoring:
            self._stop_monitoring()

    def _start_calibration(self):
        self.monitoring = False
        self.calibrating = True
        self.calibration_manager.reset()
        print("Calibration started. Keep one student centered in the camera.")

    def _stop_monitoring(self):
        self.monitoring = False
        self.calibrating = False
        self.session_analyzer.stop()
        print(f"Monitoring stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _record_alerts(self, alerts, frame):
        for alert in alerts:
            if not self.event_logger.should_log(alert["type"]):
                continue
            self.event_logger.log_event(
                event_type=alert["type"],
                message=alert["message"],
                frame=frame,
                severity=alert.get("severity", "medium"),
                confidence=alert.get("confidence"),
                risk_points=alert.get("risk_points", settings.RISK_WEIGHTS.get(alert["type"], 10)),
                category=alert.get("category"),
                recommendation=alert.get("recommendation"),
                explanation=alert.get("explanation"),
            )
        self.last_alerts = alerts or self.last_alerts[-3:]

    def _apply_runtime_sensitivity(self, alerts, risk_multiplier):
        adjusted = []
        for alert in alerts:
            item = dict(alert)
            item["risk_points"] = int(round(item.get("risk_points", settings.RISK_WEIGHTS.get(item["type"], 10)) * risk_multiplier))
            adjusted.append(item)
        return adjusted

    def _save_manual_snapshot_if_requested(self, frame):
        if not self._manual_snapshot_pending:
            return
        self.event_logger.log_event(
            event_type="manual_snapshot",
            message="Manual evidence snapshot captured by supervisor",
            frame=frame,
            severity="low",
            confidence=1.0,
            risk_points=0,
            category="Manual Review",
            recommendation="Use this snapshot as manually captured context.",
            explanation="Supervisor requested an evidence snapshot from the control interface.",
        )
        self._manual_snapshot_pending = False

    def _finish_session(self):
        self.session_analyzer.stop()
        summary = self.session_analyzer.get_summary(self.event_logger.events)
        profile = self.exam_profile.to_dict() if self.exam_profile else {}
        calibration = self.calibration_manager.summary
        exports = self.data_exporter.export(self.event_logger.events, summary, profile, calibration)
        self.event_logger.save()
        report_path = self.report_generator.generate(self.event_logger.events, summary, profile, calibration, exports)
        print(f"Final report generated: {report_path}")

    def _status_text(self):
        if self.calibrating:
            return "CALIBRATING"
        if self.monitoring:
            return "MONITORING"
        return "PAUSED"

    def _status_color(self):
        if self.calibrating:
            return (120, 220, 255)
        if self.monitoring:
            return (95, 210, 135)
        return (70, 170, 245)

    def _print_startup_message(self):
        print(settings.APP_TITLE)
        print("Mouse: Start, Stop, Calibrate, Report.")
        print("Keyboard: S start/stop, C calibrate, Q report.")
        print("Privacy note: Local educational prototype; manual review is required.")
