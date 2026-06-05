# National AI Exam Integrity Platform

Local AI-based exam monitoring prototype built with Python, OpenCV, MediaPipe fallback support, and YOLO object detection.

Created by **hz8n**.

> Privacy note: This is an educational prototype. It is not a production proctoring system and must not be used as the only evidence for academic decisions. All suspicious cases should be reviewed by a human.

## Overview

This project demonstrates a room-level AI node for a larger national exam integrity platform. It monitors a local webcam, detects suspicious exam behavior, logs evidence, calculates risk, generates reports, and exports review data.

The system is designed to be modular, explainable, and easy to expand for university projects, competitions, or research demonstrations.

## Key Features

- Live webcam monitoring.
- Beautiful OpenCV dashboard with mouse controls.
- Start, stop, calibrate, report, and manual snapshot controls.
- Face presence detection.
- Multiple-person detection.
- Frequent look-away detection.
- Low-visibility detection.
- YOLO-based object detection for people and phone-like devices.
- OpenCV fallback detection when YOLO is unavailable.
- Alert stabilization across multiple frames.
- Risk score calculation.
- Integrity Score from 0 to 100.
- Screenshot evidence for suspicious events.
- JSON and CSV export.
- Final HTML monitoring report.
- National-platform concept models for schools, rooms, cameras, sensors, sessions, and alerts.

## Tech Stack

- Python 3.12
- OpenCV
- MediaPipe
- Ultralytics YOLO
- NumPy
- HTML report generation
- JSON and CSV export

## Project Structure

```text
.
|-- main.py
|-- camera_monitor.py
|-- control_center.py
|-- dashboard_ui.py
|-- face_tracker.py
|-- object_detector.py
|-- alert_policy.py
|-- alert_stabilizer.py
|-- calibration.py
|-- event_logger.py
|-- report_generator.py
|-- data_exporter.py
|-- session_analyzer.py
|-- exam_profile.py
|-- integrity_score.py
|-- national_platform_models.py
|-- project_smoke_test.py
|-- settings.py
|-- requirements.txt
|-- NATIONAL_PLATFORM_ARCHITECTURE.md
|-- yolov8n.pt
`-- README.md
```

## Main Files

| File | Purpose |
| --- | --- |
| `main.py` | Main launcher. Checks dependencies, verifies module wiring, and starts the monitor. |
| `camera_monitor.py` | Coordinates webcam input, detection, alerts, logging, reports, and dashboard updates. |
| `control_center.py` | Central command system for keyboard shortcuts, sensitivity modes, toggles, help, and debug controls. |
| `dashboard_ui.py` | Draws the OpenCV dashboard, buttons, help overlay, debug log, and status panels. |
| `face_tracker.py` | Detects face presence, multiple faces, looking away, and low visibility. |
| `object_detector.py` | Uses YOLO and OpenCV fallback to detect people and phone-like objects. |
| `alert_policy.py` | Adds category, severity, confidence, explanation, recommendation, and risk points to alerts. |
| `alert_stabilizer.py` | Requires repeated evidence before alerts are shown or logged. |
| `calibration.py` | Collects baseline frames before monitoring starts. |
| `event_logger.py` | Saves suspicious events and screenshot evidence. |
| `session_analyzer.py` | Tracks session statistics, risk score, and timeline. |
| `integrity_score.py` | Calculates Integrity Score from 0 to 100. |
| `report_generator.py` | Generates the final HTML report. |
| `data_exporter.py` | Exports `events.csv` and `session_summary.json`. |
| `national_platform_models.py` | Demo data models for a national-scale platform. |
| `NATIONAL_PLATFORM_ARCHITECTURE.md` | Architecture proposal for national deployment. |

## Installation

Clone the repository:

```bash
git clone https://github.com/hz8n/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Start the application:

```bash
python main.py
```

Run a dependency and wiring check without opening the camera:

```bash
python main.py --check
```

Preview startup wiring without opening the camera:

```bash
python main.py --no-run
```

Use a different camera index:

```bash
python main.py --camera 1
```

## Controls

### Mouse Controls

- `Start` - starts calibration, then monitoring.
- `Stop` - stops monitoring or calibration.
- `Calibrate` - starts a new calibration.
- `Report` - exits and generates the report.

### Keyboard Controls

| Key | Action |
| --- | --- |
| `S` | Start or stop monitoring |
| `C` | Calibrate |
| `Q` | Generate report and quit |
| `P` | Capture manual evidence snapshot |
| `M` | Mute alert emphasis |
| `F` | Toggle face detection |
| `O` | Toggle object detection |
| `T` | Toggle alert stabilizer |
| `1` | Strict sensitivity |
| `2` | Balanced sensitivity |
| `3` | Review sensitivity |
| `H` | Show or hide help overlay |
| `D` | Show or hide debug command log |

## Output

After running the system, output is saved in:

```text
monitoring_output/
|-- events.json
|-- events.csv
|-- final_report.html
|-- session_summary.json
`-- screenshots/
```

Open this file in a browser:

```text
monitoring_output/final_report.html
```

## Test The Project

Run the smoke test:

```bash
python project_smoke_test.py
```

The smoke test checks that the main modules work together without opening the webcam. It creates a temporary event, exports CSV and JSON, generates a report, and draws the dashboard on a fake frame.

## Detection Layers

### Face And Behavior

- Student absent from camera view.
- More than one face visible.
- Frequent looking away.
- Low brightness or poor camera visibility.
- OpenCV fallback if MediaPipe face mesh is unavailable.

### Object Detection

- YOLO detection for `person` and `cell phone`.
- OpenCV rectangular-object fallback.
- Phone-like object evidence screenshots.

### Alert Stabilization

The system does not immediately log every one-frame detection. It uses a sliding-window stabilizer to reduce random false positives.

## Scoring

### Risk Score

Risk score measures suspicious activity intensity during the current session.

Example weights:

```python
RISK_WEIGHTS = {
    "student_absent": 35,
    "multiple_people": 40,
    "frequent_look_away": 20,
    "phone_like_object": 45,
    "low_visibility": 10,
    "ai_person_count": 35,
    "ai_cell_phone": 55,
    "manual_snapshot": 0,
}
```

### Integrity Score

Integrity Score starts at 100 and decreases based on suspicious evidence.

Labels:

- `Trusted`
- `Needs Review`
- `High Concern`
- `Critical Review`

The score is a review aid, not a final verdict.

## National Platform Concept

This prototype can be presented as a local room node for:

**National AI Exam Integrity Platform**

The national concept includes:

- Thousands of cameras.
- Interactive school map.
- Central control center.
- RF, Bluetooth, and WiFi device detection.
- Identity verification.
- Collaborative cheating detection.
- Evidence archive.
- Post-exam answer analysis.
- Human review workflow.

Read the full architecture proposal:

```text
NATIONAL_PLATFORM_ARCHITECTURE.md
```

## Limitations

- This is not a production system.
- The model can produce false positives.
- Lighting and camera angle affect accuracy.
- YOLO `yolov8n.pt` is a general model, not a custom exam-room model.
- Real deployment requires privacy, legal, cybersecurity, and bias reviews.

## Future Improvements

- Train a custom YOLO model on exam-room datasets.
- Add gaze estimation.
- Add hand gesture detection.
- Add voice and sound analysis.
- Add RF/Bluetooth/WiFi sensor integration.
- Add multi-camera 360-degree monitoring.
- Add Flask/FastAPI web dashboard.
- Add database storage.
- Add PDF report export.
- Add teacher/admin authentication.
- Add national dashboard with map view.

## Author

Built by **hz8n**.

GitHub: [https://github.com/hz8n](https://github.com/hz8n)

## License

This project is provided for educational and research purposes. Add a license file before using it in public or commercial contexts.
