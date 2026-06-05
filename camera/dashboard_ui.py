import cv2

import settings


class DashboardUI:
    """OpenCV dashboard drawing and mouse button handling."""

    def __init__(self, window_name):
        self.window_name = window_name
        self.buttons = {}
        self.mouse_position = None
        self.pending_action = None

    def attach(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self._on_mouse)

    def pop_action(self):
        action = self.pending_action
        self.pending_action = None
        return action

    def draw(self, frame, state):
        alerts = state["alerts"]
        status = state["status"]
        status_color = state["status_color"]
        h, w = frame.shape[:2]

        self._draw_panel(frame, 0, 0, w, 96, (24, 29, 38), alpha=0.9)
        self._draw_panel(frame, max(0, w - 330), 96, w, h, (19, 24, 32), alpha=0.88)
        cv2.putText(frame, settings.APP_TITLE, (20, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (250, 250, 250), 2)
        cv2.putText(frame, f"Status: {status}", (20, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.62, status_color, 2)
        cv2.putText(frame, "Local educational prototype - manual review required", (250, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (185, 195, 210), 1)

        self._draw_buttons(frame, w, state["monitoring"], state["calibrating"])
        if state["calibrating"]:
            self._draw_calibration(frame, state["calibration_progress"])
        self._draw_side_panel(frame, alerts, state, w, h, status, status_color)

    def _on_mouse(self, event, x, y, flags, param):
        self.mouse_position = (x, y)
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        for action, box in self.buttons.items():
            x1, y1, x2, y2 = box
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.pending_action = action
                return

    def _draw_calibration(self, frame, progress):
        h, w = frame.shape[:2]
        panel_right = min(w - 350, 600)
        self._draw_panel(frame, 24, 126, panel_right, 210, (34, 54, 86), alpha=0.86)
        cv2.putText(frame, "CALIBRATION", (46, 162), cv2.FONT_HERSHEY_SIMPLEX, 0.78, (130, 225, 255), 2)
        cv2.putText(frame, "Keep one student centered and visible", (46, 196), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (245, 245, 245), 1)
        bar_width = max(180, panel_right - 96)
        self._draw_progress(frame, 46, 224, bar_width, 18, progress, (95, 220, 135))
        cv2.putText(frame, f"{progress}%", (56 + bar_width, 241), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (245, 245, 245), 1)

    def _draw_buttons(self, frame, width, monitoring, calibrating):
        self.buttons = {}
        x = max(20, width - 650)
        y = 18
        specs = [
            ("start", "Start", (70, 185, 120), not monitoring and not calibrating),
            ("stop", "Stop", (70, 95, 220), monitoring or calibrating),
            ("calibrate", "Calibrate", (230, 170, 70), True),
            ("report", "Report", (120, 115, 235), True),
        ]
        for action, label, color, enabled in specs:
            self._draw_button(frame, action, label, x, y, 140, 46, color, enabled)
            x += 152

    def _draw_side_panel(self, frame, alerts, state, width, height, status, status_color):
        x = max(0, width - 310)
        risk = state["risk_score"]
        max_risk = state["max_risk_score"]

        cv2.putText(frame, "CONTROL CENTER", (x, 132), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (245, 245, 245), 2)
        cv2.putText(frame, status, (x, 164), cv2.FONT_HERSHEY_SIMPLEX, 0.66, status_color, 2)
        cv2.putText(frame, f"Risk score: {risk}/100", (x, 206), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (235, 240, 245), 1)
        self._draw_progress(frame, x, 222, 260, 18, risk, self._risk_color(risk))
        cv2.putText(frame, f"Max risk: {max_risk}/100", (x, 266), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (190, 200, 215), 1)
        cv2.putText(frame, f"Events: {state['event_count']}", (x, 292), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (190, 200, 215), 1)
        cv2.putText(frame, f"Frames: {state['frame_count']}", (x, 318), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (190, 200, 215), 1)
        cv2.putText(frame, f"Mode: {state.get('sensitivity_mode', 'balanced')}", (x, 344), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (190, 200, 215), 1)

        y = 374
        for label, value in state.get("control_cards", []):
            cv2.putText(frame, f"{label}: {value}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (180, 190, 205), 1)
            y += 20

        cv2.putText(frame, "RECENT ALERTS", (x, y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (245, 245, 245), 2)
        y += 48
        if not alerts:
            cv2.putText(frame, "No active alerts", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (155, 210, 170), 1)
        for alert in alerts[:6]:
            severity_color = (105, 110, 120) if state.get("alerts_muted") else self._severity_color(alert.get("severity", "medium"))
            self._draw_panel(frame, x - 6, y - 20, width - 18, y + 44, (34, 40, 52), alpha=0.82)
            cv2.circle(frame, (x + 8, y), 6, severity_color, -1)
            cv2.putText(frame, alert.get("type", "alert")[:26], (x + 22, y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (245, 245, 245), 1)
            self._put_wrapped_text(frame, alert.get("message", ""), x + 22, y + 24, width - x - 42, 0.38, (200, 210, 225))
            y += 74
            if y > height - 34:
                break
        if state.get("show_help"):
            self._draw_help_overlay(frame, state.get("help_lines", []))
        if state.get("show_debug"):
            self._draw_debug_overlay(frame, state)

    def _draw_button(self, frame, action, label, x, y, width, height, color, enabled=True):
        self.buttons[action] = (x, y, x + width, y + height)
        hovered = self.mouse_position and x <= self.mouse_position[0] <= x + width and y <= self.mouse_position[1] <= y + height
        bg = color if enabled else (72, 78, 88)
        if hovered and enabled:
            bg = tuple(min(255, value + 35) for value in bg)
        self._draw_panel(frame, x, y, x + width, y + height, bg, alpha=0.94)
        text_color = (255, 255, 255) if enabled else (170, 175, 185)
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
        tx = x + (width - text_size[0]) // 2
        ty = y + (height + text_size[1]) // 2 - 2
        cv2.putText(frame, label, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2)

    def _draw_panel(self, frame, x1, y1, x2, y2, color, alpha=0.75):
        overlay = frame.copy()
        cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), color, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    def _draw_progress(self, frame, x, y, width, height, value, color):
        value = max(0, min(100, int(value)))
        cv2.rectangle(frame, (x, y), (x + width, y + height), (58, 64, 74), -1)
        cv2.rectangle(frame, (x, y), (x + int(width * value / 100), y + height), color, -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (115, 125, 140), 1)

    def _risk_color(self, risk):
        if risk >= 70:
            return (70, 80, 230)
        if risk >= 35:
            return (60, 170, 240)
        return (95, 210, 135)

    def _severity_color(self, severity):
        colors = {
            "low": (95, 210, 135),
            "medium": (60, 185, 240),
            "high": (70, 80, 230),
            "critical": (80, 45, 210),
        }
        return colors.get(severity, (60, 185, 240))

    def _put_wrapped_text(self, frame, text, x, y, max_width, scale, color):
        words = text.split()
        line = ""
        for word in words:
            test = f"{line} {word}".strip()
            size = cv2.getTextSize(test, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)[0]
            if size[0] > max_width and line:
                cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1)
                y += 17
                line = word
            else:
                line = test
        if line:
            cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1)

    def _draw_help_overlay(self, frame, lines):
        h, w = frame.shape[:2]
        x1, y1 = 40, 110
        x2, y2 = min(w - 360, 650), min(h - 40, 520)
        self._draw_panel(frame, x1, y1, x2, y2, (16, 22, 32), alpha=0.92)
        y = y1 + 34
        for index, line in enumerate(lines):
            scale = 0.62 if index == 0 else 0.48
            color = (245, 245, 245) if index == 0 else (205, 215, 230)
            thickness = 2 if index == 0 else 1
            cv2.putText(frame, line, (x1 + 24, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)
            y += 28 if index == 0 else 23

    def _draw_debug_overlay(self, frame, state):
        h, w = frame.shape[:2]
        x1, y1 = 40, max(130, h - 190)
        x2, y2 = min(w - 360, 760), h - 28
        self._draw_panel(frame, x1, y1, x2, y2, (22, 30, 42), alpha=0.88)
        cv2.putText(frame, "COMMAND LOG", (x1 + 18, y1 + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (245, 245, 245), 2)
        y = y1 + 56
        for item in state.get("command_log", [])[-5:]:
            cv2.putText(frame, f"{item['time']}  {item['message']}", (x1 + 18, y), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (205, 215, 230), 1)
            y += 22
