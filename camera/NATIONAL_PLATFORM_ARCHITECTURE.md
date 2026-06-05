# National AI Exam Integrity Platform

This document describes how the local webcam prototype can be presented as the first node of a larger national exam integrity platform.

## Vision

A unified national platform monitors exam integrity across schools, universities, remote exams, and central exam halls. It combines computer vision, behavior analysis, identity verification, device detection, evidence archiving, and post-exam analytics.

The platform does not automatically punish students. It generates evidence, risk scores, and review cases for trained human supervisors.

## Core Modules

### 1. National Control Center

- Live monitoring of thousands of exam rooms.
- Search by school, governorate, exam, room, camera, or alert type.
- Interactive map of all schools and exam centers.
- Supervisor queue for high-risk incidents.
- Real-time health monitoring for cameras and sensors.

### 2. Exam Room AI Node

Each room runs a local AI node similar to this project.

Responsibilities:

- camera stream processing
- face presence detection
- multiple-person detection
- phone detection
- head movement analysis
- gaze-pattern estimation
- screenshot evidence capture
- local buffering when internet is unstable

### 3. Multi-Sensor Device Detection

The national version can connect to:

- RF scanners
- Bluetooth scanners
- WiFi scanners
- camera feeds
- optional metal/device sensors

Detected risks:

- hidden phones
- smart watches
- hidden earphones
- unauthorized routers or hotspots
- suspicious Bluetooth devices

### 4. Behavior Intelligence

Signals:

- head movement
- gaze direction
- repeated looking at one direction
- long pause duration
- writing rhythm
- suspicious synchronized movement
- repeated hand gestures

The local prototype currently implements the first stage: face, absence, look-away, people count, phone-like objects, and risk scoring.

### 5. Collaborative Cheating Detection

The national platform compares behavior across students in the same room.

Examples:

- many students look to the same corner at the same time
- repeated synchronized gestures
- similar pause/write patterns
- answer-sheet similarity after the exam

Output:

- suspected collaboration cluster
- confidence score
- timeline of shared suspicious moments

### 6. Identity Verification

Before and during the exam:

- face recognition
- voice recognition for remote exams
- ID-card validation
- random re-checks during long sessions

Detected risks:

- impersonation
- student switching
- unauthorized person in remote room

### 7. Remote Exam Integrity

For home exams:

- webcam monitoring
- screen activity analysis
- browser-lock integration
- second-screen suspicion
- phone detection
- another-person detection
- voice and room-audio signals

### 8. Post-Exam Analytics

After the exam:

- abnormal answer similarity
- suspicious score jumps
- unusual center-level performance
- repeated patterns across schools
- question-level anomaly detection

### 9. Evidence Archive

Every suspicious event stores:

- timestamp
- event type
- confidence
- risk points
- screenshot
- short video segment
- camera ID
- school ID
- room ID
- model version
- human review decision

The archive supports long-term legal review, but privacy laws and retention rules must be followed.

## Integrity Score

Each student receives an `Integrity Score` from 0 to 100.

- 85-100: Trusted
- 65-84: Needs Review
- 40-64: High Concern
- 0-39: Critical Review

The score is not a punishment. It is a triage tool to decide what needs human review.

## Suggested National Architecture

```text
Camera / Sensors
      |
      v
Room AI Node
      |
      v
School Edge Server
      |
      v
National Message Queue
      |
      v
AI Analytics Services
      |
      v
Evidence Archive + Case Management
      |
      v
National Control Center Dashboard
```

## Why This Prototype Matters

This local project demonstrates the room-level AI node:

- webcam input
- face and object detection
- alert policy
- evidence screenshots
- event logging
- risk scoring
- final reports
- CSV/JSON export

The national platform would scale this same idea across many rooms, many schools, and many sensor types.

## Ethical And Legal Requirements

A real national system must include:

- explicit legal basis
- data minimization
- encryption
- access control
- audit logs
- retention limits
- appeal process
- human review before decisions
- bias and accuracy testing
- model version tracking

## Competition Pitch

**National AI Exam Integrity Platform** is a unified system that combines video monitoring, behavior analysis, identity verification, device detection, collaborative cheating analysis, and post-exam result analytics to protect exam integrity at national scale while keeping human review at the center.

