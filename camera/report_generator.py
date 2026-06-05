import html
import os
from collections import Counter
from datetime import datetime

import settings


class ReportGenerator:
    """Creates a simple HTML report after monitoring ends."""

    def __init__(self, output_dir=settings.OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, events, session_summary=None, exam_profile=None, calibration_summary=None, exports=None):
        report_path = os.path.join(self.output_dir, "final_report.html")
        counts = Counter(event["type"] for event in events)
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_summary = session_summary or {}
        exam_profile = exam_profile or {}
        calibration_summary = calibration_summary or {}
        exports = exports or {}

        rows = []
        for event in events:
            screenshot = html.escape(self._report_relative_path(event["screenshot"]))
            rows.append(
                "<tr>"
                f"<td>{html.escape(event['timestamp'])}</td>"
                f"<td>{html.escape(event['severity'])}</td>"
                f"<td>{html.escape(str(event.get('category', 'General')))}</td>"
                f"<td>{html.escape(str(event.get('confidence', '')))}</td>"
                f"<td>{html.escape(str(event.get('risk_points', 0)))}</td>"
                f"<td>{html.escape(event['type'])}</td>"
                f"<td>{html.escape(event['message'])}</td>"
                f"<td>{html.escape(str(event.get('recommendation', 'Manual review required.')))}</td>"
                f"<td><a href='{screenshot}'>Evidence</a></td>"
                "</tr>"
            )

        summary_items = "".join(
            f"<li><strong>{html.escape(event_type)}</strong>: {count}</li>"
            for event_type, count in counts.items()
        ) or "<li>No suspicious events recorded.</li>"

        category_items = self._list_items(session_summary.get("category_counts", {}))
        severity_items = self._list_items(session_summary.get("severity_counts", {}))
        timeline_bars = self._timeline_bars(session_summary.get("risk_timeline", []))

        html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Exam Monitoring Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; line-height: 1.45; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .note {{ padding: 12px; background: #fff4cc; border-left: 4px solid #d29b00; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 18px 0; }}
    .card {{ border: 1px solid #ddd; padding: 14px; background: #fafafa; }}
    .value {{ font-size: 24px; font-weight: bold; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .panel {{ border: 1px solid #ddd; padding: 16px; margin: 14px 0; }}
    .timeline {{ display: flex; align-items: end; gap: 3px; height: 90px; border-bottom: 1px solid #ccc; padding-top: 12px; }}
    .bar {{ width: 8px; background: #3a7ca5; }}
    .small {{ color: #666; font-size: 13px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 18px; }}
    th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
    th {{ background: #f2f2f2; }}
  </style>
</head>
<body>
  <h1>Exam Monitoring Report</h1>
  <p>Generated at: {html.escape(generated_at)}</p>
  <p class="note">Privacy note: This is only a local educational prototype. It should not be used as a final disciplinary or production proctoring system.</p>
  <div class="grid">
    <div class="panel">
      <h2>Exam Profile</h2>
      <p><strong>Student:</strong> {html.escape(str(exam_profile.get('student_name', '')))}</p>
      <p><strong>Student ID:</strong> {html.escape(str(exam_profile.get('student_id', '')))}</p>
      <p><strong>Course:</strong> {html.escape(str(exam_profile.get('course_name', '')))}</p>
      <p><strong>Exam:</strong> {html.escape(str(exam_profile.get('exam_name', '')))}</p>
      <p><strong>Instructor:</strong> {html.escape(str(exam_profile.get('instructor_name', '')))}</p>
      <p><strong>Room / Camera:</strong> {html.escape(str(exam_profile.get('room_name', '')))}</p>
    </div>
    <div class="panel">
      <h2>Calibration</h2>
      <p><strong>Completed:</strong> {html.escape(str(calibration_summary.get('calibrated', False)))}</p>
      <p><strong>Samples:</strong> {html.escape(str(calibration_summary.get('samples', 0)))}</p>
      <p><strong>Average brightness:</strong> {html.escape(str(calibration_summary.get('avg_brightness', 'N/A')))}</p>
      <p><strong>Average face size:</strong> {html.escape(str(calibration_summary.get('avg_face_width', 'N/A')))} x {html.escape(str(calibration_summary.get('avg_face_height', 'N/A')))}</p>
    </div>
  </div>
  <div class="cards">
    <div class="card"><div>Integrity score</div><div class="value">{html.escape(str(session_summary.get('integrity_score', 100)))}/100</div></div>
    <div class="card"><div>Integrity label</div><div class="value">{html.escape(str(session_summary.get('integrity_label', 'Trusted')))}</div></div>
    <div class="card"><div>Risk label</div><div class="value">{html.escape(str(session_summary.get('risk_label', 'Clear')))}</div></div>
    <div class="card"><div>Max risk score</div><div class="value">{html.escape(str(session_summary.get('max_risk_score', 0)))}/100</div></div>
    <div class="card"><div>Total alerts</div><div class="value">{html.escape(str(session_summary.get('alert_count', len(events))))}</div></div>
    <div class="card"><div>Duration</div><div class="value">{html.escape(str(session_summary.get('duration_seconds', 0)))}s</div></div>
  </div>
  <h2>Summary</h2>
  <div class="grid">
    <div class="panel"><h3>Event Types</h3><ul>{summary_items}</ul></div>
    <div class="panel"><h3>Categories</h3><ul>{category_items}</ul></div>
  </div>
  <div class="panel"><h3>Severity</h3><ul>{severity_items}</ul></div>
  <div class="panel">
    <h2>Risk Timeline</h2>
    <div class="timeline">{timeline_bars}</div>
    <p class="small">Bars show sampled risk score over the session. Higher bars indicate more suspicious activity.</p>
  </div>
  <div class="panel">
    <h2>Exported Files</h2>
    <p><strong>Events CSV:</strong> {html.escape(str(exports.get('events_csv', '')))}</p>
    <p><strong>Session JSON:</strong> {html.escape(str(exports.get('session_summary', '')))}</p>
  </div>
  <h2>Events</h2>
  <table>
    <thead>
      <tr><th>Timestamp</th><th>Severity</th><th>Category</th><th>Confidence</th><th>Risk</th><th>Type</th><th>Message</th><th>Recommendation</th><th>Screenshot</th></tr>
    </thead>
    <tbody>
      {''.join(rows) if rows else '<tr><td colspan="9">No events recorded.</td></tr>'}
    </tbody>
  </table>
</body>
</html>
"""

        with open(report_path, "w", encoding="utf-8") as file:
            file.write(html_doc)
        return report_path

    def _report_relative_path(self, path):
        if not path:
            return ""
        return os.path.relpath(path, self.output_dir).replace("\\", "/")

    def _list_items(self, values):
        if not values:
            return "<li>No data recorded.</li>"
        return "".join(
            f"<li><strong>{html.escape(str(key))}</strong>: {html.escape(str(value))}</li>"
            for key, value in values.items()
        )

    def _timeline_bars(self, timeline):
        if not timeline:
            return "<span class='small'>No risk timeline recorded.</span>"
        latest = timeline[-80:]
        bars = []
        for point in latest:
            height = max(3, min(88, int(point.get("score", 0) * 0.88)))
            title = html.escape(f"Frame {point.get('frame')}: score {point.get('score')}")
            bars.append(f"<div class='bar' title='{title}' style='height:{height}px'></div>")
        return "".join(bars)
