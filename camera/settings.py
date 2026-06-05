APP_TITLE = "AI Exam Monitoring System - Educational Prototype"
WINDOW_NAME = "AI Exam Monitoring System"
PROMPT_EXAM_PROFILE = False

CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

OUTPUT_DIR = "monitoring_output"
SCREENSHOT_DIR = "screenshots"

EVENT_COOLDOWN_SECONDS = 5
ENABLE_YOLO_OBJECT_DETECTION = True
YOLO_MODEL = "yolov8n.pt"
YOLO_CONFIDENCE = 0.35
YOLO_PROCESS_EVERY_N_FRAMES = 3

FACE_DETECTION_CONFIDENCE = 0.55
FACE_TRACKING_CONFIDENCE = 0.55

LOOK_AWAY_WINDOW_FRAMES = 60
LOOK_AWAY_ALERT_THRESHOLD = 32
LOOK_AWAY_HORIZONTAL_RATIO = 0.18
LOOK_AWAY_VERTICAL_RATIO = 0.28

ABSENCE_GRACE_FRAMES = 12
MULTIPLE_PEOPLE_GRACE_FRAMES = 8
ALERT_STABILITY_WINDOW = 18
ALERT_STABILITY_MIN_HITS = {
    "student_absent": 10,
    "multiple_people": 5,
    "frequent_look_away": 8,
    "phone_like_object": 3,
    "low_visibility": 12,
}

PHONE_MIN_AREA = 2500
PHONE_MAX_AREA = 45000
PHONE_MIN_ASPECT = 1.45
PHONE_MAX_ASPECT = 3.2
PHONE_MIN_FILL_RATIO = 0.45

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
