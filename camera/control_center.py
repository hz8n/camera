from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ControlState:
    """Runtime controls changed from dashboard buttons or keyboard shortcuts."""

    monitoring_enabled: bool = False
    calibration_requested: bool = False
    report_requested: bool = False
    manual_snapshot_requested: bool = False
    alerts_muted: bool = False
    show_help: bool = False
    show_debug: bool = False
    enable_face_detection: bool = True
    enable_object_detection: bool = True
    enable_stabilizer: bool = True
    sensitivity_mode: str = "balanced"
    command_log: list = field(default_factory=list)


class ControlCenter:
    """Central command router for the monitoring system.

    This class keeps UI and keyboard commands away from the camera loop. It gives
    the project a more professional control surface: modes, toggles, command log,
    help overlay, and explicit actions.
    """

    SENSITIVITY_PROFILES = {
        "strict": {
            "name": "Strict",
            "description": "Faster alerts, useful for demos with obvious suspicious actions.",
            "stability_scale": 0.65,
            "risk_multiplier": 1.25,
        },
        "balanced": {
            "name": "Balanced",
            "description": "Default balance between sensitivity and false positives.",
            "stability_scale": 1.0,
            "risk_multiplier": 1.0,
        },
        "review": {
            "name": "Review",
            "description": "Conservative mode, fewer alerts and more human-review oriented.",
            "stability_scale": 1.35,
            "risk_multiplier": 0.85,
        },
    }

    KEY_ACTIONS = {
        ord("s"): "toggle_monitoring",
        ord("c"): "calibrate",
        ord("q"): "report",
        ord("h"): "toggle_help",
        ord("d"): "toggle_debug",
        ord("m"): "toggle_mute",
        ord("f"): "toggle_face",
        ord("o"): "toggle_objects",
        ord("t"): "toggle_stabilizer",
        ord("1"): "mode_strict",
        ord("2"): "mode_balanced",
        ord("3"): "mode_review",
        ord("p"): "snapshot",
    }

    def __init__(self):
        self.state = ControlState()
        self._log("System ready")

    def handle_action(self, action):
        if not action:
            return []

        messages = []
        if action == "start":
            self.state.monitoring_enabled = True
            self.state.calibration_requested = True
            messages.append("Calibration requested before monitoring")
        elif action == "stop":
            self.state.monitoring_enabled = False
            self.state.calibration_requested = False
            messages.append("Monitoring stopped")
        elif action == "toggle_monitoring":
            if self.state.monitoring_enabled or self.state.calibration_requested:
                messages.extend(self.handle_action("stop"))
            else:
                messages.extend(self.handle_action("start"))
        elif action == "calibrate":
            self.state.monitoring_enabled = False
            self.state.calibration_requested = True
            messages.append("Calibration requested")
        elif action == "report":
            self.state.report_requested = True
            messages.append("Report requested")
        elif action == "snapshot":
            self.state.manual_snapshot_requested = True
            messages.append("Manual evidence snapshot requested")
        elif action == "toggle_mute":
            self.state.alerts_muted = not self.state.alerts_muted
            messages.append(f"Alerts muted: {self.state.alerts_muted}")
        elif action == "toggle_help":
            self.state.show_help = not self.state.show_help
            messages.append(f"Help overlay: {self.state.show_help}")
        elif action == "toggle_debug":
            self.state.show_debug = not self.state.show_debug
            messages.append(f"Debug overlay: {self.state.show_debug}")
        elif action == "toggle_face":
            self.state.enable_face_detection = not self.state.enable_face_detection
            messages.append(f"Face detection: {self.state.enable_face_detection}")
        elif action == "toggle_objects":
            self.state.enable_object_detection = not self.state.enable_object_detection
            messages.append(f"Object detection: {self.state.enable_object_detection}")
        elif action == "toggle_stabilizer":
            self.state.enable_stabilizer = not self.state.enable_stabilizer
            messages.append(f"Alert stabilizer: {self.state.enable_stabilizer}")
        elif action == "mode_strict":
            messages.append(self.set_sensitivity("strict"))
        elif action == "mode_balanced":
            messages.append(self.set_sensitivity("balanced"))
        elif action == "mode_review":
            messages.append(self.set_sensitivity("review"))
        else:
            messages.append(f"Unknown action: {action}")

        for message in messages:
            self._log(message)
        return messages

    def handle_key(self, key):
        action = self.KEY_ACTIONS.get(key)
        if action:
            return self.handle_action(action)
        return []

    def set_sensitivity(self, mode):
        if mode not in self.SENSITIVITY_PROFILES:
            return f"Unknown sensitivity mode: {mode}"
        self.state.sensitivity_mode = mode
        return f"Sensitivity mode changed to {self.SENSITIVITY_PROFILES[mode]['name']}"

    def consume_calibration_request(self):
        requested = self.state.calibration_requested
        self.state.calibration_requested = False
        return requested

    def consume_report_request(self):
        requested = self.state.report_requested
        self.state.report_requested = False
        return requested

    def consume_snapshot_request(self):
        requested = self.state.manual_snapshot_requested
        self.state.manual_snapshot_requested = False
        return requested

    def active_profile(self):
        return self.SENSITIVITY_PROFILES[self.state.sensitivity_mode]

    def status_cards(self):
        profile = self.active_profile()
        return [
            ("Mode", profile["name"]),
            ("Face", "ON" if self.state.enable_face_detection else "OFF"),
            ("Objects", "ON" if self.state.enable_object_detection else "OFF"),
            ("Stabilizer", "ON" if self.state.enable_stabilizer else "OFF"),
            ("Mute", "ON" if self.state.alerts_muted else "OFF"),
        ]

    def help_lines(self):
        return [
            "Keyboard Shortcuts",
            "S - start / stop monitoring",
            "C - recalibrate",
            "Q - generate report",
            "P - manual evidence snapshot",
            "M - mute dashboard alert emphasis",
            "F - toggle face detection",
            "O - toggle object detection",
            "T - toggle alert stabilizer",
            "1 - strict sensitivity",
            "2 - balanced sensitivity",
            "3 - review sensitivity",
            "H - show / hide this help",
            "D - show / hide debug overlay",
        ]

    def _log(self, message):
        self.state.command_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message,
        })
        self.state.command_log = self.state.command_log[-8:]
