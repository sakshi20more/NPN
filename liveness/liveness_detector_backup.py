

# # import cv2
# # import dlib
# # import numpy as np
# # import face_recognition_models


# # # ============================================================
# # # CONFIGURATION
# # # ============================================================

# # EAR_THRESHOLD = 0.21
# # BLINK_CONSECUTIVE_FRAMES = 2


# # # ============================================================
# # # DLIB SETUP
# # # ============================================================

# # PREDICTOR_PATH = (
# #     face_recognition_models.pose_predictor_model_location()
# # )

# # _detector = dlib.get_frontal_face_detector()
# # _predictor = dlib.shape_predictor(PREDICTOR_PATH)


# # # ============================================================
# # # EYE ASPECT RATIO
# # # ============================================================

# # def calculate_eye_aspect_ratio(eye_points):
# #     """
# #     Calculate Eye Aspect Ratio (EAR).
# #     """

# #     eye_points = np.asarray(
# #         eye_points,
# #         dtype=np.float64
# #     )

# #     vertical_1 = np.linalg.norm(
# #         eye_points[1] - eye_points[5]
# #     )

# #     vertical_2 = np.linalg.norm(
# #         eye_points[2] - eye_points[4]
# #     )

# #     horizontal = np.linalg.norm(
# #         eye_points[0] - eye_points[3]
# #     )

# #     if horizontal == 0:
# #         return 0.0

# #     return (
# #         vertical_1 + vertical_2
# #     ) / (2.0 * horizontal)


# # # ============================================================
# # # GET EYE LANDMARKS
# # # ============================================================

# # def get_eye_points(shape):

# #     left_eye = [
# #         (shape.part(i).x, shape.part(i).y)
# #         for i in range(36, 42)
# #     ]

# #     right_eye = [
# #         (shape.part(i).x, shape.part(i).y)
# #         for i in range(42, 48)
# #     ]

# #     return left_eye, right_eye


# # # ============================================================
# # # CHECK BLINK FROM ONE FRAME
# # # ============================================================

# # def check_blink(frame, blink_frames=0):
# #     """
# #     Process ONE camera frame.

# #     Returns:

# #         blink_detected
# #         updated_blink_frames
# #     """

# #     gray = cv2.cvtColor(
# #         frame,
# #         cv2.COLOR_BGR2GRAY
# #     )

# #     faces = _detector(gray, 0)

# #     # No face
# #     if len(faces) == 0:
# #         return False, 0

# #     # Multiple faces
# #     if len(faces) > 1:
# #         return False, 0

# #     face = faces[0]

# #     shape = _predictor(
# #         gray,
# #         face
# #     )

# #     left_eye, right_eye = get_eye_points(
# #         shape
# #     )

# #     left_ear = calculate_eye_aspect_ratio(
# #         left_eye
# #     )

# #     right_ear = calculate_eye_aspect_ratio(
# #         right_eye
# #     )

# #     average_ear = (
# #         left_ear + right_ear
# #     ) / 2.0

# #     # Eyes closed
# #     if average_ear < EAR_THRESHOLD:

# #         blink_frames += 1

# #     else:

# #         # Eyes opened after being closed
# #         if blink_frames >= BLINK_CONSECUTIVE_FRAMES:

# #             return True, 0

# #         blink_frames = 0

# #     return False, blink_frames


# # # ============================================================
# # # LIVENESS STATE
# # # ============================================================

# # class LivenessDetector:
# #     """
# #     Maintains liveness state across camera frames.
# #     """

# #     def __init__(self):

# #         self.blink_frames = 0
# #         self.live = False

# #     def process_frame(self, frame):
# #         """
# #         Process one frame and update liveness state.

# #         Returns:
# #             True when a blink has been detected.
# #         """

# #         if self.live:
# #             return True

# #         blink_detected, self.blink_frames = check_blink(
# #             frame,
# #             self.blink_frames
# #         )

# #         if blink_detected:
# #             self.live = True

# #         return self.live

# #     def reset(self):

# #         self.blink_frames = 0
# #         self.live = False

# import cv2
# import dlib
# import numpy as np
# import face_recognition_models


# # ============================================================
# # CONFIGURATION
# # ============================================================

# EAR_THRESHOLD = 0.21
# BLINK_CONSECUTIVE_FRAMES = 2

# # Minimum vertical movement in pixels
# HEAD_MOVEMENT_THRESHOLD = 15

# # Number of frames required to confirm movement
# MOVEMENT_REQUIRED_FRAMES = 2


# # ============================================================
# # DLIB SETUP
# # ============================================================

# PREDICTOR_PATH = (
#     face_recognition_models.pose_predictor_model_location()
# )

# face_detector = dlib.get_frontal_face_detector()
# landmark_predictor = dlib.shape_predictor(PREDICTOR_PATH)


# # ============================================================
# # EYE ASPECT RATIO
# # ============================================================

# def calculate_eye_aspect_ratio(eye_points):

#     eye_points = np.asarray(
#         eye_points,
#         dtype=np.float64
#     )

#     vertical_1 = np.linalg.norm(
#         eye_points[1] - eye_points[5]
#     )

#     vertical_2 = np.linalg.norm(
#         eye_points[2] - eye_points[4]
#     )

#     horizontal = np.linalg.norm(
#         eye_points[0] - eye_points[3]
#     )

#     if horizontal == 0:
#         return 0.0

#     return (
#         vertical_1 + vertical_2
#     ) / (2.0 * horizontal)


# # ============================================================
# # GET EYE LANDMARKS
# # ============================================================

# def get_eye_points(shape):

#     left_eye = [
#         (shape.part(i).x, shape.part(i).y)
#         for i in range(36, 42)
#     ]

#     right_eye = [
#         (shape.part(i).x, shape.part(i).y)
#         for i in range(42, 48)
#     ]

#     return left_eye, right_eye


# # ============================================================
# # GET FACE CENTER
# # ============================================================

# def get_face_center(face):

#     center_x = (
#         face.left() + face.right()
#     ) // 2

#     center_y = (
#         face.top() + face.bottom()
#     ) // 2

#     return center_x, center_y


# # ============================================================
# # LIVENESS DETECTOR
# # ============================================================

# class LivenessDetector:

#     def __init__(self):

#         self.reset()

#     # ========================================================
#     # RESET
#     # ========================================================

#     def reset(self):

#         # -----------------------------
#         # Blink
#         # -----------------------------

#         self.blink_frames = 0
#         self.blink_detected = False

#         # -----------------------------
#         # Head movement
#         # -----------------------------

#         self.previous_y = None

#         self.up_frames = 0
#         self.down_frames = 0

#         self.head_up_detected = False
#         self.head_down_detected = False

#         # -----------------------------
#         # Final state
#         # -----------------------------

#         self.live = False

#         self.stage = "BLINK"

#         self.reason = (
#             "Please blink once."
#         )

#     # ========================================================
#     # BLINK DETECTION
#     # ========================================================

#     def detect_blink(self, shape):

#         left_eye, right_eye = get_eye_points(
#             shape
#         )

#         left_ear = calculate_eye_aspect_ratio(
#             left_eye
#         )

#         right_ear = calculate_eye_aspect_ratio(
#             right_eye
#         )

#         average_ear = (
#             left_ear + right_ear
#         ) / 2.0

#         # Eyes are closed
#         if average_ear < EAR_THRESHOLD:

#             self.blink_frames += 1

#         else:

#             # Eyes opened after being closed
#             if (
#                 self.blink_frames
#                 >= BLINK_CONSECUTIVE_FRAMES
#             ):

#                 self.blink_detected = True

#             self.blink_frames = 0

#         return self.blink_detected

#     # ========================================================
#     # GET VERTICAL MOVEMENT
#     # ========================================================

#     def get_vertical_movement(self, face):

#         _, current_y = get_face_center(
#             face
#         )

#         if self.previous_y is None:

#             self.previous_y = current_y

#             return 0

#         movement_y = (
#             current_y - self.previous_y
#         )

#         self.previous_y = current_y

#         return movement_y

#     # ========================================================
#     # DETECT HEAD UP
#     # ========================================================

#     def detect_head_up(self, face):

#         movement_y = self.get_vertical_movement(
#             face
#         )

#         # In an OpenCV image:
#         #
#         # Y decreases when the face moves UP.
#         #
#         # Therefore negative movement means UP.

#         if movement_y <= -HEAD_MOVEMENT_THRESHOLD:

#             self.up_frames += 1

#         else:

#             self.up_frames = max(
#                 0,
#                 self.up_frames - 1
#             )

#         if (
#             self.up_frames
#             >= MOVEMENT_REQUIRED_FRAMES
#         ):

#             self.head_up_detected = True

#         return self.head_up_detected

#     # ========================================================
#     # DETECT HEAD DOWN
#     # ========================================================

#     def detect_head_down(self, face):

#         movement_y = self.get_vertical_movement(
#             face
#         )

#         # Positive Y movement means DOWN.

#         if movement_y >= HEAD_MOVEMENT_THRESHOLD:

#             self.down_frames += 1

#         else:

#             self.down_frames = max(
#                 0,
#                 self.down_frames - 1
#             )

#         if (
#             self.down_frames
#             >= MOVEMENT_REQUIRED_FRAMES
#         ):

#             self.head_down_detected = True

#         return self.head_down_detected

#     # ========================================================
#     # PROCESS FRAME
#     # ========================================================

#     def process_frame(self, frame):

#         """
#         Liveness sequence:

#             1. Blink
#             2. Move head UP
#             3. Move head DOWN
#             4. Live

#         Returns:

#             {
#                 "live": bool,
#                 "stage": str,
#                 "reason": str,
#                 "face_count": int
#             }
#         """

#         gray = cv2.cvtColor(
#             frame,
#             cv2.COLOR_BGR2GRAY
#         )

#         faces = face_detector(
#             gray,
#             0
#         )

#         # ----------------------------------------------------
#         # NO FACE
#         # ----------------------------------------------------

#         if len(faces) == 0:

#             self.reason = (
#                 "No face detected."
#             )

#             return {
#                 "live": False,
#                 "stage": self.stage,
#                 "reason": self.reason,
#                 "face_count": 0
#             }

#         # ----------------------------------------------------
#         # MULTIPLE FACES
#         # ----------------------------------------------------

#         if len(faces) > 1:

#             self.reason = (
#                 "Multiple faces detected. "
#                 "Only one person should be visible."
#             )

#             return {
#                 "live": False,
#                 "stage": self.stage,
#                 "reason": self.reason,
#                 "face_count": len(faces)
#             }

#         # ----------------------------------------------------
#         # ONE FACE
#         # ----------------------------------------------------

#         face = faces[0]

#         shape = landmark_predictor(
#             gray,
#             face
#         )

#         # ----------------------------------------------------
#         # STAGE 1 — BLINK
#         # ----------------------------------------------------

#         if self.stage == "BLINK":

#             self.detect_blink(shape)

#             if self.blink_detected:

#                 self.stage = "HEAD_UP"

#                 # Reset movement tracking
#                 self.previous_y = None
#                 self.up_frames = 0

#                 self.reason = (
#                     "Blink detected. "
#                     "Please move your head UP."
#                 )

#             else:

#                 self.reason = (
#                     "Please blink once."
#                 )

#         # ----------------------------------------------------
#         # STAGE 2 — HEAD UP
#         # ----------------------------------------------------

#         elif self.stage == "HEAD_UP":

#             self.detect_head_up(face)

#             if self.head_up_detected:

#                 self.stage = "HEAD_DOWN"

#                 # Reset movement tracking
#                 self.previous_y = None
#                 self.down_frames = 0

#                 self.reason = (
#                     "Head UP detected. "
#                     "Please move your head DOWN."
#                 )

#             else:

#                 self.reason = (
#                     "Please move your head UP."
#                 )

#         # ----------------------------------------------------
#         # STAGE 3 — HEAD DOWN
#         # ----------------------------------------------------

#         elif self.stage == "HEAD_DOWN":

#             self.detect_head_down(face)

#             if self.head_down_detected:

#                 self.stage = "COMPLETE"

#                 self.live = True

#                 self.reason = (
#                     "Liveness verification passed."
#                 )

#             else:

#                 self.reason = (
#                     "Please move your head DOWN."
#                 )

#         # ----------------------------------------------------
#         # COMPLETE
#         # ----------------------------------------------------

#         elif self.stage == "COMPLETE":

#             self.live = True

#             self.reason = (
#                 "Liveness verification passed."
#             )

#         return {
#             "live": self.live,
#             "stage": self.stage,
#             "reason": self.reason,
#             "face_count": 1
#         }


# # ============================================================
# # STANDALONE TEST
# # ============================================================

# def test_liveness():

#     print()
#     print("===================================")
#     print("       LIVENESS / ANTI-SPOOF")
#     print("===================================")
#     print()

#     print("Step 1: Blink once.")
#     print("Step 2: Move your head UP.")
#     print("Step 3: Move your head DOWN.")
#     print()
#     print("Press Q to cancel.")
#     print()

#     detector = LivenessDetector()

#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():

#         print(
#             "❌ Camera could not be opened."
#         )

#         return

#     while True:

#         ret, frame = cap.read()

#         if not ret:

#             print(
#                 "❌ Could not read camera frame."
#             )

#             break

#         result = detector.process_frame(
#             frame
#         )

#         # ----------------------------------------------------
#         # DISPLAY INSTRUCTION
#         # ----------------------------------------------------

#         cv2.putText(
#             frame,
#             result["reason"],
#             (20, 40),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.65,
#             (0, 255, 0),
#             2
#         )

#         # ----------------------------------------------------
#         # DISPLAY STAGE
#         # ----------------------------------------------------

#         cv2.putText(
#             frame,
#             f"Stage: {result['stage']}",
#             (20, 80),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.65,
#             (255, 255, 0),
#             2
#         )

#         # ----------------------------------------------------
#         # DISPLAY LIVE STATUS
#         # ----------------------------------------------------

#         cv2.putText(
#             frame,
#             f"Live: {result['live']}",
#             (20, 120),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.7,
#             (0, 255, 0),
#             2
#         )

#         cv2.imshow(
#             "Liveness / Anti-Spoof Test",
#             frame
#         )

#         # ----------------------------------------------------
#         # SUCCESS
#         # ----------------------------------------------------

#         if result["live"]:

#             print()
#             print("===================================")
#             print("       LIVENESS PASSED")
#             print("===================================")
#             print()
#             print("✅ Blink detected")
#             print("✅ Head UP detected")
#             print("✅ Head DOWN detected")
#             print("✅ Liveness verification passed")
#             print()

#             break

#         # ----------------------------------------------------
#         # QUIT
#         # ----------------------------------------------------

#         if (
#             cv2.waitKey(1) & 0xFF
#             == ord("q")
#         ):

#             print()
#             print(
#                 "❌ Liveness cancelled."
#             )

#             break

#     cap.release()
#     cv2.destroyAllWindows()


# # ============================================================
# # MAIN
# # ============================================================

# if __name__ == "__main__":

#     test_liveness()

import cv2
import dlib
import numpy as np
import face_recognition_models
import os

# ============================================================
# 68-POINT FACE LANDMARK MODEL
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

LANDMARK_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "shape_predictor_68_face_landmarks.dat",
    "shape_predictor_68_face_landmarks.dat"
)

landmark_predictor = dlib.shape_predictor(
    LANDMARK_MODEL_PATH
)


# ============================================================
# CONFIGURATION
# ============================================================

EAR_THRESHOLD = 0.21
BLINK_CONSECUTIVE_FRAMES = 2

HEAD_MOVEMENT_THRESHOLD = 25
HEAD_MOVEMENT_TARGET = 0.08

MOVEMENT_REQUIRED_FRAMES = 2

# ============================================================
# DLIB SETUP
# ============================================================

PREDICTOR_PATH = (
    face_recognition_models.pose_predictor_model_location()
)

face_detector = dlib.get_frontal_face_detector()

landmark_predictor = dlib.shape_predictor(
    PREDICTOR_PATH
)


# ============================================================
# EYE ASPECT RATIO
# ============================================================

def calculate_eye_aspect_ratio(eye_points):

    eye_points = np.asarray(
        eye_points,
        dtype=np.float64
    )

    vertical_1 = np.linalg.norm(
        eye_points[1] - eye_points[5]
    )

    vertical_2 = np.linalg.norm(
        eye_points[2] - eye_points[4]
    )

    horizontal = np.linalg.norm(
        eye_points[0] - eye_points[3]
    )

    if horizontal == 0:
        return 0.0

    return (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)


# ============================================================
# GET EYE POINTS
# ============================================================

def get_eye_points(shape):

    left_eye = [
        (shape.part(i).x, shape.part(i).y)
        for i in range(36, 42)
    ]

    right_eye = [
        (shape.part(i).x, shape.part(i).y)
        for i in range(42, 48)
    ]

    return left_eye, right_eye


# ============================================================
# GET FACE CENTER
# ============================================================

def get_face_center(face):

    center_x = (
        face.left() + face.right()
    ) / 2.0

    center_y = (
        face.top() + face.bottom()
    ) / 2.0

    return center_x, center_y

def get_pose_ratio(shape):
    """
    Calculate normalized nose position using
    68 facial landmarks.

    This is relative to the eyes, so moving
    the entire photo should have much less effect.
    """
def check_face_consistency(self, shape):
    """
        Check whether the facial landmarks changed
        significantly from the previous frame.
        """

    current_points = np.array(
        [
            (shape.part(i).x, shape.part(i).y)
            for i in range(68)
        ],
        dtype=np.float32
    )

    if self.previous_landmarks is None:
        self.previous_landmarks = current_points
        return True

    left_eye = current_points[36]
    right_eye = current_points[45]

    eye_distance = np.linalg.norm(
        right_eye - left_eye
    )

    if eye_distance < 1.0:
        return False

    movement = np.mean(
        np.linalg.norm(
            current_points
            - self.previous_landmarks,
            axis=1
        )
    )

    normalized_movement = (
        movement / eye_distance
    )

    self.previous_landmarks = current_points

    if normalized_movement > 0.35:
        self.face_change_detected = True
        return False

    
    # 68 landmark points
    points = np.array(
        [
            (shape.part(i).x, shape.part(i).y)
            for i in range(68)
        ],
        dtype=np.float32
    )

    # Left eye: 36-41
    left_eye_center = np.mean(
        points[36:42],
        axis=0
    )

    # Right eye: 42-47
    right_eye_center = np.mean(
        points[42:48],
        axis=0
    )

    # Nose: landmark 30
    nose = points[30]

    # Distance between the eyes
    eye_distance = np.linalg.norm(
        right_eye_center - left_eye_center
    )

    if eye_distance < 1.0:
        return None

    # Normalize nose position relative to eyes
    eye_center = (
        left_eye_center + right_eye_center
    ) / 2.0

    vertical_ratio = (
        nose[1] - eye_center[1]
    ) / eye_distance

    return float(vertical_ratio)


# ============================================================
# LIVENESS DETECTOR
# ============================================================

class LivenessDetector:

    def __init__(self):

        self.reset()

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        # ----------------------------------------------------
        # FACE CONSISTENCY
        # ----------------------------------------------------

        self.previous_landmarks = None
        self.face_change_detected = False

        # ----------------------------------------------------
        # BLINK
        # ----------------------------------------------------
        

        self.blink_frames = 0
        self.blink_detected = False
        self.max_blink_frames = 0

        # ----------------------------------------------------
        # HEAD UP
        # ----------------------------------------------------
        self.initial_y = None
        self.up_frames = 0
        self.head_up_detected = False
        self.max_upward_movement = 0.0

        # ----------------------------------------------------
        # HEAD DOWN
        # ----------------------------------------------------

        self.up_y = None
        self.down_frames = 0
        self.head_down_detected = False
        self.max_downward_movement = 0.0

        # ----------------------------------------------------
        # FINAL STATE
        # ----------------------------------------------------

        self.live = False

        self.stage = "BLINK"

        self.reason = (
            "BLINK ONCE"
        )

    # ========================================================
    # BLINK DETECTION
    # ========================================================

    def detect_blink(self, shape):

        left_eye, right_eye = get_eye_points(
            shape
        )

        left_ear = calculate_eye_aspect_ratio(
            left_eye
        )

        right_ear = calculate_eye_aspect_ratio(
            right_eye
        )

        average_ear = (
            left_ear + right_ear
        ) / 2.0

        # Eyes closed
        if average_ear < EAR_THRESHOLD:

            self.blink_frames += 1

            self.max_blink_frames = max(
            self.max_blink_frames,
            self.blink_frames
    )

        else:

            # Eyes opened after being closed
            if (
                self.blink_frames
                >= BLINK_CONSECUTIVE_FRAMES
            ):

                self.blink_detected = True

            self.blink_frames = 0

        return self.blink_detected

    # ========================================================
    # HEAD UP
    # ========================================================

    def detect_head_up(self, shape):

        current_ratio = get_pose_ratio(
            shape
        )

        if current_ratio is None:
            return False

        # Record initial facial geometry
        if self.initial_y is None:

            self.initial_y = current_ratio

            return False

        # Change in normalized nose position
        upward_movement = (
            self.initial_y - current_ratio
        )

        self.max_upward_movement = max(
            self.max_upward_movement,
            abs(upward_movement)
        )

        # Normalized movement threshold
        if upward_movement >= 0.08:

            self.up_frames += 1

        else:

            self.up_frames = 0

        if self.up_frames >= MOVEMENT_REQUIRED_FRAMES:

            self.head_up_detected = True

            self.up_y = current_ratio

        return self.head_up_detected

    # ========================================================
    # HEAD DOWN
    # ========================================================

    def detect_head_down(self, shape):

        current_ratio = get_pose_ratio(
            shape
        )

        if current_ratio is None:
            return False

        if self.up_y is None:

            self.up_y = current_ratio

            return False

        downward_movement = (
            current_ratio - self.up_y
        )

        self.max_downward_movement = max(
            self.max_downward_movement,
            abs(downward_movement)
        )

        if downward_movement >= 0.08:

            self.down_frames += 1

        else:

            self.down_frames = 0

        if self.down_frames >= MOVEMENT_REQUIRED_FRAMES:

            self.head_down_detected = True

        return self.head_down_detected
    # ========================================================
    # PROCESS FRAME
    # ========================================================

    def process_frame(self, frame):

        """
        Process one camera frame.

        Sequence:

            BLINK
              ↓
            HEAD UP
              ↓
            HEAD DOWN
              ↓
            COMPLETE
        """

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector(
            gray,
            0
        )

        # ----------------------------------------------------
        # NO FACE
        # ----------------------------------------------------

        if len(faces) == 0:

            return {
                "live": False,
                "stage": self.stage,
                "reason": self.reason,
                "face_count": 0
            }

        # ----------------------------------------------------
        # MULTIPLE FACES
        # ----------------------------------------------------

        if len(faces) > 1:

            return {
                "live": False,
                "stage": self.stage,
                "reason": (
                    "Only ONE face should be visible."
                ),
                "face_count": len(faces)
            }

        # ----------------------------------------------------
        # ONE FACE
        # ----------------------------------------------------

        face = faces[0]

        shape = landmark_predictor(
            gray,
            face
        )

        # ====================================================
        # STAGE 1 — BLINK
        # ====================================================

        if self.stage == "BLINK":

            self.detect_blink(shape)

            if self.blink_detected:

                self.stage = "HEAD_UP"

                self.initial_y = None
                self.up_frames = 0

                self.reason = (
                    "BLINK DETECTED\n"
                    "NOW MOVE HEAD UP"
                )

            else:

                self.reason = (
                    "BLINK ONCE"
                )

        # ====================================================
        # STAGE 2 — HEAD UP
        # ====================================================

        elif self.stage == "HEAD_UP":

            self.detect_head_up(
                shape
            )

            if self.head_up_detected:

                self.stage = "HEAD_DOWN"

                self.down_frames = 0

                self.reason = (
                    "HEAD UP DETECTED\n"
                    "NOW MOVE HEAD DOWN"
                )

            else:

                self.reason = (
                    "MOVE HEAD UP"
                )

        # ====================================================
        # STAGE 3 — HEAD DOWN
        # ====================================================

        elif self.stage == "HEAD_DOWN":

            self.detect_head_down(
                shape
            )

            if self.head_down_detected:

                self.stage = "COMPLETE"

                self.live = True

                self.reason = (
                    "LIVENESS PASSED"
                )

            else:

                self.reason = (
                    "MOVE HEAD DOWN"
                )

        # ====================================================
        # COMPLETE
        # ====================================================

        elif self.stage == "COMPLETE":

            self.live = True

            self.reason = (
                "LIVENESS PASSED"
            )

        return {
    "live": self.live,
    "stage": self.stage,
    "reason": self.reason,
    "face_count": 1,

    "blink_detected": bool(
        self.blink_detected
    ),

    "head_up_detected": bool(
        self.head_up_detected
    ),

    "head_down_detected": bool(
        self.head_down_detected
    ),

    "blink_frames": int(
    self.max_blink_frames
),

"head_up_movement": float(
    self.max_upward_movement
),

"head_down_movement": float(
    self.max_downward_movement
),

"liveness_score": float(
    0.30 * min(
        1.0,
        self.max_blink_frames / 3.0
    )
    + 0.35 * min(
        1.0,
        self.max_upward_movement
        / HEAD_MOVEMENT_TARGET
    )
    + 0.35 * min(
        1.0,
        self.max_downward_movement
        / HEAD_MOVEMENT_TARGET
    )
)

}


# ============================================================
# DISPLAY INSTRUCTION
# ============================================================

def draw_liveness_instruction(
    frame,
    result
):

    height, width = frame.shape[:2]

    # --------------------------------------------------------
    # Top banner
    # --------------------------------------------------------

    cv2.rectangle(
        frame,
        (0, 0),
        (width, 145),
        (0, 0, 0),
        -1
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    cv2.putText(
        frame,
        "LIVENESS / ANTI-SPOOF",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2
    )

    # --------------------------------------------------------
    # Instruction
    # --------------------------------------------------------

    reason = result["reason"]

    if reason == "BLINK ONCE":

        instruction = "BLINK ONCE"

    elif reason == "MOVE HEAD UP":

        instruction = "MOVE YOUR HEAD UP"

    elif reason == "MOVE HEAD DOWN":

        instruction = "MOVE YOUR HEAD DOWN"

    elif reason == "LIVENESS PASSED":

        instruction = "LIVENESS PASSED"

    elif reason == "BLINK DETECTED\nNOW MOVE HEAD UP":

        instruction = "NOW MOVE YOUR HEAD UP"

    elif reason == "HEAD UP DETECTED\nNOW MOVE HEAD DOWN":

        instruction = "NOW MOVE YOUR HEAD DOWN"

    else:

        instruction = reason.replace(
            "\n",
            " "
        )

    # --------------------------------------------------------
    # Large instruction
    # --------------------------------------------------------

    cv2.putText(
        frame,
        instruction,
        (20, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 255),
        2
    )

    # --------------------------------------------------------
    # Stage
    # --------------------------------------------------------

    cv2.putText(
        frame,
        f"Stage: {result['stage']}",
        (20, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (200, 200, 200),
        1
    )

    return frame


# ============================================================
# STANDALONE TEST
# ============================================================

def test_liveness():

    print()
    print("===================================")
    print("       LIVENESS / ANTI-SPOOF")
    print("===================================")
    print()
    print("Follow the instructions on screen:")
    print()
    print("  1. BLINK ONCE")
    print("  2. MOVE YOUR HEAD UP")
    print("  3. MOVE YOUR HEAD DOWN")
    print()
    print("Press Q to cancel.")
    print()

    detector = LivenessDetector()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print(
            "❌ Camera could not be opened."
        )

        return

    previous_stage = None

    try:

        while True:

            ret, frame = cap.read()

            if not ret:

                print(
                    "❌ Could not read camera."
                )

                break

            result = detector.process_frame(
                frame
            )

            # ------------------------------------------------
            # Print stage changes
            # ------------------------------------------------

            if (
                result["stage"]
                != previous_stage
            ):

                print(
                    f"➡ {result['reason']}"
                )

                previous_stage = (
                    result["stage"]
                )

            # ------------------------------------------------
            # Draw UI
            # ------------------------------------------------

            frame = draw_liveness_instruction(
                frame,
                result
            )

            cv2.imshow(
                "Liveness / Anti-Spoof",
                frame
            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if result["live"]:

                print()
                print(
                    "==================================="
                )
                print(
                    "       LIVENESS PASSED"
                )
                print(
                    "==================================="
                )
                print(
                    "✅ Blink detected"
                )
                print(
                    "✅ Head UP detected"
                )
                print(
                    "✅ Head DOWN detected"
                )
                print()
                print("===== LIVENESS MEASUREMENTS =====")

                print(
                    f"Blink frames       : "
                    f"{result.get('blink_frames', 0)}"
                )

                print(
                    f"Head up movement   : "
                    f"{result.get('head_up_movement', 0.0):.2f}"
                )

                print(
                    f"Head down movement : "
                    f"{result.get('head_down_movement', 0.0):.2f}"
                )

                print("=================================")

               

                # ========================================================
                # LIVENESS COMPONENT SCORES
                # ========================================================

                blink_frames = result.get(
                    "blink_frames",
                    0
                )

                head_up_movement = result.get(
                    "head_up_movement",
                    0.0
                )

                head_down_movement = result.get(
                    "head_down_movement",
                    0.0
                )

                # Blink score
                blink_score = min(
                    1.0,
                    blink_frames / 3.0
                )

                # Head movement scores
                head_up_score = min(
                    1.0,
                    head_up_movement
                    / HEAD_MOVEMENT_TARGET
                )

                head_down_score = min(
                    1.0,
                    head_down_movement
                    / HEAD_MOVEMENT_TARGET
                )
                # Combined liveness score
                liveness_score = (
                    0.30 * blink_score
                    + 0.35 * head_up_score
                    + 0.35 * head_down_score
                )
                

                print()
                print("===== COMPONENT SCORES =====")

                print(
                    f"Blink score       : "
                    f"{blink_score:.3f}"
                )

                print(
                    f"Head UP score     : "
                    f"{head_up_score:.3f}"
                )

                print(
                    f"Head DOWN score   : "
                    f"{head_down_score:.3f}"
                )
                print(
                    f"Liveness score    : "
                    f"{liveness_score:.3f}"
)

                print("============================")

                break

            # ------------------------------------------------
            # QUIT
            # ------------------------------------------------

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):

                print()
                print(
                    "❌ Liveness cancelled."
                )

                break

    finally:

        cap.release()

        cv2.destroyAllWindows()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test_liveness()