import cv2
import mediapipe as mp
from utils import calculate_ear
from pygame import mixer
import time
from collections import deque

# Initialize mixer
mixer.init()
mixer.music.load("alarm.wav")

# Improved FaceMesh (IMPORTANT 🔥)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Tuned thresholds (better accuracy)
EAR_THRESHOLD = 0.23
CLOSED_FRAMES = 25

# Counters
counter = 0
blink_count = 0
blink_flag = False

# Smart alarm control
last_alert_time = 0
ALERT_INTERVAL = 3

# EAR smoothing (VERY IMPORTANT 🔥)
ear_buffer = deque(maxlen=5)


def play_alarm():
    if not mixer.music.get_busy():
        mixer.music.play()


def process_frame(frame):
    global counter, blink_count, blink_flag, last_alert_time

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            h, w, _ = frame.shape

            left_eye = []
            right_eye = []

            # LEFT EYE
            for idx in LEFT_EYE:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                left_eye.append((x, y))

            # RIGHT EYE
            for idx in RIGHT_EYE:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                right_eye.append((x, y))

            # Draw eye points (optional but useful)
            for (x, y) in left_eye:
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)

            for (x, y) in right_eye:
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)

            # 🔥 Smooth EAR (major accuracy boost)
            current_ear = (calculate_ear(left_eye) + calculate_ear(right_eye)) / 2.0
            ear_buffer.append(current_ear)
            ear = sum(ear_buffer) / len(ear_buffer)

            # Show EAR
            cv2.putText(frame, f"EAR: {ear:.2f}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Blink detection
            if ear < EAR_THRESHOLD:
                if not blink_flag:
                    blink_count += 1
                    blink_flag = True
                counter += 1
            else:
                blink_flag = False
                counter = 0

            # Show blink count
            cv2.putText(frame, f"Blinks: {blink_count}", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Status detection
            status = "AWAKE"
            color = (0, 255, 0)

            current_time = time.time()

            if counter > CLOSED_FRAMES:
                status = "DROWSY"
                color = (0, 0, 255)

                if current_time - last_alert_time > ALERT_INTERVAL:
                    play_alarm()
                    last_alert_time = current_time

            cv2.putText(frame, f"Status: {status}", (30, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # Face bounding box
            x_min = int(min([lm.x for lm in face_landmarks.landmark]) * w)
            y_min = int(min([lm.y for lm in face_landmarks.landmark]) * h)
            x_max = int(max([lm.x for lm in face_landmarks.landmark]) * w)
            y_max = int(max([lm.y for lm in face_landmarks.landmark]) * h)

            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

    return frame, status, blink_count