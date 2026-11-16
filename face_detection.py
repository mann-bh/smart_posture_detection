
import cv2
import mediapipe as mp
import math

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Webcam not accessible")
    exit()

print("Iris measurement started. Press Q to exit.")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    height, width, _ = frame.shape

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            # Get iris landmarks
            p469 = face_landmarks.landmark[469]
            p471 = face_landmarks.landmark[471]

            p474 = face_landmarks.landmark[474]
            p476 = face_landmarks.landmark[476]

            # Convert normalized coordinates to pixels
            x469, y469 = int(p469.x * width), int(p469.y * height)
            x471, y471 = int(p471.x * width), int(p471.y * height)

            x474, y474 = int(p474.x * width), int(p474.y * height)
            x476, y476 = int(p476.x * width), int(p476.y * height)

            # Calculate first iris width
            P1 = math.hypot(
                x471 - x469,
                y471 - y469
            )

            # Calculate second iris width
            P2 = math.hypot(
                x476 - x474,
                y476 - y474
            )

            # Average iris width
            P = (P1 + P2) / 2

            # Draw iris points
            for x, y in [
                (x469, y469),
                (x471, y471),
                (x474, y474),
                (x476, y476)
            ]:
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            # Display measurements
            cv2.putText(
                frame,
                f"Eye 1: {P1:.2f} px",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Eye 2: {P2:.2f} px",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Average Iris Width: {P:.2f} px",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    cv2.imshow("Iris Width Measurement", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
face_mesh.close()
cv2.destroyAllWindows()
