
import math


# --------------------------------
# PROJECT CONFIGURATION
# --------------------------------

BASELINE_DISTANCE_CM = 50

HEAD_TILT_THRESHOLD = 10

LEAN_THRESHOLD_RATIO = 0.85


# --------------------------------
# HEAD TILT DETECTION
# --------------------------------

def calculate_head_tilt(
    face_landmarks,
    frame_width,
    frame_height
):

    # Extract eye corner landmarks
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]

    # Convert normalized coordinates to pixels
    x1 = left_eye.x * frame_width
    y1 = left_eye.y * frame_height

    x2 = right_eye.x * frame_width
    y2 = right_eye.y * frame_height

    # Calculate horizontal and vertical differences
    dx = x2 - x1
    dy = y2 - y1

    # Avoid division or invalid geometry
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return None

    # Calculate angle in degrees
    angle = math.degrees(
        math.atan2(dy, dx)
    )

    # Normalize angle to -90 to +90 degrees
    if angle > 90:
        angle -= 180

    elif angle < -90:
        angle += 180

    return angle


# --------------------------------
# HEAD TILT CLASSIFICATION
# --------------------------------

def detect_head_tilt(angle):

    if angle is None:
        return "UNKNOWN"

    if abs(angle) > HEAD_TILT_THRESHOLD:
        return "HEAD TILTED"

    return "NORMAL"


# --------------------------------
# FORWARD LEAN DETECTION
# --------------------------------

def detect_forward_lean(
    current_distance,
    baseline_distance=BASELINE_DISTANCE_CM
):

    if current_distance is None:
        return "UNKNOWN"

    lean_threshold = (
        baseline_distance * LEAN_THRESHOLD_RATIO
    )

    if current_distance < lean_threshold:
        return "LEANING FORWARD"

    return "NORMAL"


# --------------------------------
# COMPLETE POSTURE ANALYSIS
# --------------------------------

def analyze_posture(
    face_landmarks,
    frame_width,
    frame_height,
    current_distance
):

    # Calculate head tilt
    angle = calculate_head_tilt(
        face_landmarks,
        frame_width,
        frame_height
    )

    # Classify head position
    head_status = detect_head_tilt(angle)

    # Detect forward leaning
    lean_status = detect_forward_lean(
        current_distance
    )

    return angle, head_status, lean_status
