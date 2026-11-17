
import cv2
import mediapipe as mp
import math
from collections import deque
from timer import ScreenTimeManager
from time_alert import DistanceAlertManager
from posture import analyze_posture
from exercise_tips import get_exercise_tip, get_break_exercise
from data_logger import log_data


# -----------------------------
# PROJECT CONFIGURATION
# -----------------------------

IRIS_WIDTH_CM = 1.17
KNOWN_DISTANCE_CM = 50

CALIBRATION_FRAMES = 30
SMOOTHING_WINDOW = 10

distance_history = deque(maxlen=SMOOTHING_WINDOW)


# -----------------------------
# INITIALIZE MEDIAPIPE
# -----------------------------

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# -----------------------------
# INITIALIZE WEBCAM
# -----------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Webcam not accessible")
    face_mesh.close()
    raise SystemExit

focal_length = None

calibration_samples = []
collecting = False


# -----------------------------
# INITIALIZE DISTANCE ALERTS
# -----------------------------

alert_manager = DistanceAlertManager(
    too_close=40,
    too_far=80,
    persistence_seconds=5,
    cooldown_seconds=30
)


# -----------------------------
# DAY 7: INITIALIZE SCREEN TIMER
# -----------------------------

screen_timer = ScreenTimeManager(
    break_interval_minutes=.1
)


# -----------------------------
# PROJECT START
# -----------------------------

print("SMART POSTURE MONITOR")
print("---------------------")
print("Sit exactly 50 cm from webcam.")
print("Press C to calibrate.")
print("Press B after taking a break to reset timer.")
print("Press Q to exit.")


# -----------------------------
# MAIN LOOP
# -----------------------------

while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame")
        break

    height, width, _ = frame.shape

    rgb_frame = cv2.cvtColor(
        frame, cv2.COLOR_BGR2RGB
    )

    results = face_mesh.process(rgb_frame)

    # Initialize frame variables
    iris_width = None
    raw_distance = None
    smooth_distance = None

    head_tilt_angle = None
    head_status = "WAITING FOR FACE"
    lean_status = "WAITING FOR DISTANCE"

    distance_status = "WAITING FOR FACE"


    # -----------------------------
    # FACE AND IRIS DETECTION
    # -----------------------------

    if results.multi_face_landmarks:

        face_landmarks = results.multi_face_landmarks[0]

        p469 = face_landmarks.landmark[469]
        p471 = face_landmarks.landmark[471]

        p474 = face_landmarks.landmark[474]
        p476 = face_landmarks.landmark[476]

        P1 = math.hypot(
            (p471.x - p469.x) * width,
            (p471.y - p469.y) * height
        )

        P2 = math.hypot(
            (p476.x - p474.x) * width,
            (p476.y - p474.y) * height
        )

        iris_width = (P1 + P2) / 2


        # -----------------------------
        # DRAW IRIS LANDMARKS
        # -----------------------------

        for index in [469, 471, 474, 476]:

            landmark = face_landmarks.landmark[index]

            x = int(landmark.x * width)
            y = int(landmark.y * height)

            cv2.circle(
                frame,
                (x, y),
                4,
                (0, 255, 0),
                -1
            )


        # -----------------------------
        # CALIBRATION
        # -----------------------------

        if collecting and iris_width > 0:

            calibration_samples.append(iris_width)

            if len(calibration_samples) >= CALIBRATION_FRAMES:

                average_width = (
                    sum(calibration_samples)
                    / len(calibration_samples)
                )

                focal_length = (
                    average_width * KNOWN_DISTANCE_CM
                ) / IRIS_WIDTH_CM

                collecting = False

                distance_history.clear()

                print("\nCalibration successful!")
                print(
                    f"Average iris width: {average_width:.2f} px"
                )
                print(
                    f"Focal length: {focal_length:.2f} px"
                )


        # -----------------------------
        # DISTANCE ESTIMATION
        # -----------------------------

        if (
            focal_length is not None
            and iris_width is not None
            and iris_width > 0
            and not collecting
        ):

            raw_distance = (
                IRIS_WIDTH_CM * focal_length
            ) / iris_width

            if 15 <= raw_distance <= 150:

                distance_history.append(raw_distance)

                smooth_distance = (
                    sum(distance_history)
                    / len(distance_history)
                )


        # -----------------------------
        # DAY 6: POSTURE ANALYSIS
        # -----------------------------

        head_tilt_angle, head_status, lean_status = analyze_posture(
            face_landmarks,
            width,
            height,
            smooth_distance
        )


    # -----------------------------
    # DAY 5: DISTANCE ALERT SYSTEM
    # -----------------------------

    distance_status = alert_manager.update(
        smooth_distance
    )


    # -----------------------------
    # DAY 7: SCREEN-TIME TRACKING
    # -----------------------------

    screen_time = screen_timer.get_screen_time()

    break_due = screen_timer.check_break_time()

    formatted_screen_time = screen_timer.format_time(
        screen_time
    )


    # -----------------------------
    # DAY 8: CSV DATA LOGGING
    # -----------------------------

    log_data(
        distance=smooth_distance,
        head_tilt=head_tilt_angle,
        head_status=head_status,
        lean_status=lean_status,
        screen_time=screen_time,
        break_reminder=break_due
    )


    # -----------------------------
    # DISPLAY IRIS WIDTH
    # -----------------------------

    if iris_width is not None:

        cv2.putText(
            frame,
            f"Iris Width: {iris_width:.2f} px",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2
        )


    # -----------------------------
    # DISPLAY CALIBRATION
    # -----------------------------

    if collecting:

        cv2.putText(
            frame,
            f"Calibrating: {len(calibration_samples)}/{CALIBRATION_FRAMES}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 0),
            2
        )

    elif focal_length is None:

        cv2.putText(
            frame,
            "Press C to calibrate",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 255),
            2
        )

    elif smooth_distance is not None:

        cv2.putText(
            frame,
            f"Raw Distance: {raw_distance:.2f} cm",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Smooth Distance: {smooth_distance:.2f} cm",
            (20, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            frame,
            "Distance unavailable",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 255),
            2
        )


    # -----------------------------
    # DISPLAY DISTANCE STATUS
    # -----------------------------

    if distance_status == "NORMAL":
        status_color = (0, 255, 0)

    elif distance_status == "TOO CLOSE":
        status_color = (0, 0, 255)

    elif distance_status == "TOO FAR":
        status_color = (0, 165, 255)

    else:
        status_color = (255, 255, 255)

    cv2.putText(
        frame,
        f"Status: {distance_status}",
        (20, 155),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        status_color,
        2
    )


    # -----------------------------
    # DAY 6: DISPLAY HEAD TILT
    # -----------------------------

    if head_tilt_angle is not None:

        tilt_text = (
            f"Head Tilt: {head_tilt_angle:.1f} deg"
            f" | {head_status}"
        )

    else:

        tilt_text = "Head Tilt: Unavailable"

    if head_status == "HEAD TILTED":
        tilt_color = (0, 0, 255)

    elif head_status == "NORMAL":
        tilt_color = (0, 255, 0)

    else:
        tilt_color = (255, 255, 255)

    cv2.putText(
        frame,
        tilt_text,
        (20, 195),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        tilt_color,
        2
    )


    # -----------------------------
    # DAY 6: DISPLAY FORWARD LEAN
    # -----------------------------

    if lean_status == "LEANING FORWARD":
        lean_color = (0, 0, 255)

    elif lean_status == "NORMAL":
        lean_color = (0, 255, 0)

    else:
        lean_color = (255, 255, 255)

    cv2.putText(
        frame,
        f"Posture: {lean_status}",
        (20, 235),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        lean_color,
        2
    )


    # -----------------------------
    # DAY 7: DISPLAY SCREEN TIME
    # -----------------------------

    cv2.putText(
        frame,
        f"Screen Time: {formatted_screen_time}",
        (20, 275),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # -----------------------------
    # DAY 7: DISPLAY BREAK REMINDER
    # -----------------------------

    if break_due:

        cv2.putText(
            frame,
            "BREAK TIME! Take a short break.",
            (20, 315),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 255),
            2
        )


    # -----------------------------
    # DAY 8: EXERCISE RECOMMENDATIONS
    # -----------------------------

    if head_status == "HEAD TILTED" or lean_status == "LEANING FORWARD":

        exercise_tip = get_exercise_tip(
            head_status,
            lean_status
        )

        cv2.putText(
            frame,
            "Exercise Recommendation:",
            (20, 355),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 165, 255),
            2
        )

        cv2.putText(
            frame,
            exercise_tip[:55],
            (20, 390),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2
        )

    elif break_due:

        break_tip = get_break_exercise()

        cv2.putText(
            frame,
            "Break Exercise:",
            (20, 355),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 165, 255),
            2
        )

        cv2.putText(
            frame,
            break_tip[:55],
            (20, 390),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2
        )


    # -----------------------------
    # DISPLAY WEBCAM
    # -----------------------------

    cv2.imshow("Smart Posture Monitor", frame)


    # -----------------------------
    # KEYBOARD CONTROLS
    # -----------------------------

    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):

        if iris_width is not None and iris_width > 0:

            calibration_samples = []
            distance_history.clear()
            focal_length = None
            collecting = True

            print("Calibration started. Stay still!")

        else:

            print("Face not detected. Try again.")

    elif key == ord('b'):

        screen_timer.reset_timer()

        print("Break completed! Screen-time timer reset.")

    elif key == ord('q'):
        break


# -----------------------------
# CLEANUP
# -----------------------------

cap.release()
face_mesh.close()
cv2.destroyAllWindows()

print("Distance monitoring stopped.")
