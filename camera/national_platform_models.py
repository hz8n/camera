from dataclasses import asdict, dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class SensorDevice:
    sensor_id: str
    sensor_type: str
    room_id: str
    status: str = "online"


@dataclass
class ExamCamera:
    camera_id: str
    room_id: str
    stream_url: str
    angle: str = "front"
    status: str = "online"


@dataclass
class ExamRoom:
    room_id: str
    school_id: str
    name: str
    capacity: int
    cameras: list = field(default_factory=list)
    sensors: list = field(default_factory=list)


@dataclass
class School:
    school_id: str
    name: str
    governorate: str
    latitude: float
    longitude: float
    rooms: list = field(default_factory=list)


@dataclass
class NationalExamSession:
    session_id: str
    exam_name: str
    school_id: str
    room_id: str
    started_at: str
    status: str = "running"


@dataclass
class NationalAlert:
    alert_id: str
    session_id: str
    school_id: str
    room_id: str
    alert_type: str
    severity: str
    message: str
    integrity_score: int
    created_at: str
    human_review_required: bool = True


def build_demo_national_topology():
    """Creates sample data for a national dashboard prototype."""
    school = School(
        school_id="SCH-001",
        name="Demo National School",
        governorate="Amman",
        latitude=31.9539,
        longitude=35.9106,
    )
    room = ExamRoom(room_id="ROOM-101", school_id=school.school_id, name="Hall A", capacity=35)
    room.cameras = [
        asdict(ExamCamera("CAM-101-FRONT", room.room_id, "local://camera/0", "front")),
        asdict(ExamCamera("CAM-101-SIDE", room.room_id, "local://camera/1", "side")),
        asdict(ExamCamera("CAM-101-BACK", room.room_id, "local://camera/2", "back")),
    ]
    room.sensors = [
        asdict(SensorDevice("RF-101", "rf_scanner", room.room_id)),
        asdict(SensorDevice("BT-101", "bluetooth_scanner", room.room_id)),
        asdict(SensorDevice("WIFI-101", "wifi_scanner", room.room_id)),
    ]
    school.rooms.append(asdict(room))

    session = NationalExamSession(
        session_id=str(uuid4()),
        exam_name="National Final Exam",
        school_id=school.school_id,
        room_id=room.room_id,
        started_at=datetime.now().isoformat(timespec="seconds"),
    )
    return {
        "schools": [asdict(school)],
        "active_sessions": [asdict(session)],
    }

