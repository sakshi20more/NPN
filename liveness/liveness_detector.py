# import cv2
# import dlib
# import numpy as np
# import face_recognition_models


# # ============================================================
# # CONFIGURATION
# # ============================================================

# # Number of consecutive frames in which the eyes must
# # appear closed to count as a blink.
# BLINK_CONSECUTIVE_FRAMES = 2

# # Eye Aspect Ratio threshold.
# # Lower EAR = eyes more closed.
# EAR_THRESHOLD = 0.21

# # Camera
# CAMERA_INDEX = 0


# # ============================================================
# # DLIB SETUP
# # ============================================================

# # face_recognition package normally uses the same
# # 68-point facial landmark model internally.
# #
# # We need the landmark predictor file for explicit
# # eye landmark detection.


# PREDICTOR_PATH = (
#     face_recognition_models.pose_predictor_model_location()
# )


# # ============================================================
# # EYE ASPECT RATIO
# # ============================================================

# def calculate_eye_aspect_ratio(eye_points):
#     """
#     Calculate Eye Aspect Ratio (EAR).

#     eye_points:
#         Six (x, y) points representing one eye.

#     Returns:
#         EAR value.
#     """

#     eye_points = np.asarray(
#         eye_points,
#         dtype=np.float64
#     )

#     # Vertical distances
#     vertical_1 = np.linalg.norm(
#         eye_points[1] - eye_points[5]
#     )

#     vertical_2 = np.linalg.norm(
#         eye_points[2] - eye_points[4]
#     )

#     # Horizontal distance
#     horizontal = np.linalg.norm(
#         eye_points[0] - eye_points[3]
#     )

#     # Avoid division by zero
#     if horizontal == 0:
#         return 0.0

#     ear = (
#         vertical_1 + vertical_2
#     ) / (2.0 * horizontal)

#     return float(ear)


# # ============================================================
# # LANDMARK EXTRACTION
# # ============================================================

# def get_eye_points(shape):
#     """
#     Extract left and right eye landmarks
#     from dlib's 68 facial landmarks.

#     Returns:
#         left_eye, right_eye
#     """

#     # dlib landmark indexes:
#     #
#     # Left eye  = 36 - 41
#     # Right eye = 42 - 47

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
# # BLINK DETECTION
# # ============================================================

# def detect_blink(
#     detector,
#     predictor,
#     frame,
#     blink_frames
# ):
#     """
#     Check whether a blink is occurring.

#     Returns:
#         blink_detected, updated_blink_frames
#     """

#     gray = cv2.cvtColor(
#         frame,
#         cv2.COLOR_BGR2GRAY
#     )

#     faces = detector(gray, 0)

#     # No face
#     if len(faces) == 0:
#         return False, 0

#     # For liveness, we require exactly one face.
#     if len(faces) > 1:
#         return False, 0

#     face = faces[0]

#     shape = predictor(
#         gray,
#         face
#     )

#     left_eye, right_eye = get_eye_points(
#         shape
#     )

#     left_ear = calculate_eye_aspect_ratio(
#         left_eye
#     )

#     right_ear = calculate_eye_aspect_ratio(
#         right_eye
#     )

#     average_ear = (
#         left_ear + right_ear
#     ) / 2.0

#     # --------------------------------------------------------
#     # Eyes closed
#     # --------------------------------------------------------

#     if average_ear < EAR_THRESHOLD:

#         blink_frames += 1

#     else:

#         # If the eyes were closed for enough frames
#         # and are now open, count it as a blink.

#         if blink_frames >= BLINK_CONSECUTIVE_FRAMES:

#             return True, 0

#         blink_frames = 0

#     return False, blink_frames


# # ============================================================
# # MAIN LIVENESS CHECK
# # ============================================================

# def check_liveness(
#     camera_index=CAMERA_INDEX
# ):
#     """
#     Perform a simple blink-based liveness check.

#     The user must blink while facing the camera.

#     Returns:
#         Dictionary containing:
#             live
#             reason
#     """

#     # --------------------------------------------------------
#     # Load dlib models
#     # --------------------------------------------------------

#     detector = dlib.get_frontal_face_detector()

#     try:

#         predictor = dlib.shape_predictor(
#             PREDICTOR_PATH
#         )

#     except RuntimeError:

#         print(
#             "\n❌ Facial landmark model not found."
#         )

#         print(
#             f"Expected file:"
#         )

#         print(
#             f"{PREDICTOR_PATH}"
#         )

#         return {
#             "live": False,
#             "reason": "Landmark model not found"
#         }

#     # --------------------------------------------------------
#     # Open camera
#     # --------------------------------------------------------

#     cap = cv2.VideoCapture(
#         camera_index
#     )

#     if not cap.isOpened():

#         return {
#             "live": False,
#             "reason": "Camera could not be opened"
#         }

#     print("\n===================================")
#     print("          LIVENESS CHECK")
#     print("===================================")

#     print(
#         "\nLook directly at the camera."
#     )

#     print(
#         "Please blink once."
#     )

#     print(
#         "Press Q to cancel."
#     )

#     blink_frames = 0

#     live = False

#     # --------------------------------------------------------
#     # Camera loop
#     # --------------------------------------------------------

#     while True:

#         ret, frame = cap.read()

#         if not ret:

#             break

#         blink_detected, blink_frames = detect_blink(
#             detector,
#             predictor,
#             frame,
#             blink_frames
#         )

#         # ----------------------------------------------------
#         # Display status
#         # ----------------------------------------------------

#         display_frame = frame.copy()

#         cv2.putText(
#             display_frame,
#             "Please blink",
#             (20, 40),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.9,
#             (0, 255, 0),
#             2
#         )

#         cv2.imshow(
#             "Liveness Detection",
#             display_frame
#         )

#         # ----------------------------------------------------
#         # Blink detected
#         # ----------------------------------------------------

#         if blink_detected:

#             print(
#                 "\n✅ Blink detected."
#             )

#             print(
#                 "✅ Liveness check passed."
#             )

#             live = True

#             break

#         # ----------------------------------------------------
#         # Quit
#         # ----------------------------------------------------

#         key = cv2.waitKey(1) & 0xFF

#         if key == ord("q"):

#             print(
#                 "\n❌ Liveness check cancelled."
#             )

#             break

#     # --------------------------------------------------------
#     # Cleanup
#     # --------------------------------------------------------

#     cap.release()
#     cv2.destroyAllWindows()

#     # --------------------------------------------------------
#     # Return result
#     # --------------------------------------------------------

#     if live:

#         return {
#             "live": True,
#             "reason": "Blink detected"
#         }

#     return {
#         "live": False,
#         "reason": "Blink not detected"
#     }


# # ============================================================
# # LOCAL TEST
# # ============================================================

# if __name__ == "__main__":

#     result = check_liveness()

#     print("\n===================================")
#     print("       LIVENESS RESULT")
#     print("===================================")

#     print(
#         f"Live   : {result['live']}"
#     )

#     print(
#         f"Reason : {result['reason']}"
#     )

import cv2
import dlib
import numpy as np
import face_recognition_models


# ============================================================
# CONFIGURATION
# ============================================================

EAR_THRESHOLD = 0.21
BLINK_CONSECUTIVE_FRAMES = 2


# ============================================================
# DLIB SETUP
# ============================================================

PREDICTOR_PATH = (
    face_recognition_models.pose_predictor_model_location()
)

_detector = dlib.get_frontal_face_detector()
_predictor = dlib.shape_predictor(PREDICTOR_PATH)


# ============================================================
# EYE ASPECT RATIO
# ============================================================

def calculate_eye_aspect_ratio(eye_points):
    """
    Calculate Eye Aspect Ratio (EAR).
    """

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
# GET EYE LANDMARKS
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
# CHECK BLINK FROM ONE FRAME
# ============================================================

def check_blink(frame, blink_frames=0):
    """
    Process ONE camera frame.

    Returns:

        blink_detected
        updated_blink_frames
    """

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = _detector(gray, 0)

    # No face
    if len(faces) == 0:
        return False, 0

    # Multiple faces
    if len(faces) > 1:
        return False, 0

    face = faces[0]

    shape = _predictor(
        gray,
        face
    )

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

        blink_frames += 1

    else:

        # Eyes opened after being closed
        if blink_frames >= BLINK_CONSECUTIVE_FRAMES:

            return True, 0

        blink_frames = 0

    return False, blink_frames


# ============================================================
# LIVENESS STATE
# ============================================================

class LivenessDetector:
    """
    Maintains liveness state across camera frames.
    """

    def __init__(self):

        self.blink_frames = 0
        self.live = False

    def process_frame(self, frame):
        """
        Process one frame and update liveness state.

        Returns:
            True when a blink has been detected.
        """

        if self.live:
            return True

        blink_detected, self.blink_frames = check_blink(
            frame,
            self.blink_frames
        )

        if blink_detected:
            self.live = True

        return self.live

    def reset(self):

        self.blink_frames = 0
        self.live = False