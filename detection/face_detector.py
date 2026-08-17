import os
import cv2
from ultralytics import YOLO


# ============================================================
# YOLO FACE MODEL
# ============================================================

MODEL_PATH = os.path.join(
    "models",
    "yolov9t-face-lindevs.pt"
)

face_model = YOLO(MODEL_PATH)


# ============================================================
# DETECT FACES
# ============================================================

def detect_faces(frame, confidence=0.3):
    """
    Detect faces using YOLOv9t-Face.

    Args:
        frame:
            OpenCV BGR image.

        confidence:
            Minimum YOLO confidence.

    Returns:
        face_locations:
            Face locations in the format expected by
            face_recognition:

            (top, right, bottom, left)

        rgb_frame:
            RGB version of the frame.

        yolo_confidences:
            Confidence score for each detected face.
    """

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Run YOLO
    results = face_model(
        frame,
        conf=confidence,
        verbose=False
    )

    face_locations = []
    yolo_confidences = []

    # Process detections
    for result in results:

        for box in result.boxes:

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            confidence_score = float(
                box.conf[0]
            )

            # face_recognition format:
            # (top, right, bottom, left)

            face_locations.append(
                (
                    y1,
                    x2,
                    y2,
                    x1
                )
            )

            yolo_confidences.append(
                confidence_score
            )

    return (
        face_locations,
        rgb_frame,
        yolo_confidences
    )


# ============================================================
# DRAW FACE BOXES
# ============================================================

def draw_face_boxes(
    frame,
    face_locations,
    yolo_confidences=None
):
    """
    Draw YOLO face boxes and confidence values.
    """

    if yolo_confidences is None:
        yolo_confidences = [
            None
        ] * len(face_locations)

    for face_location, confidence in zip(
        face_locations,
        yolo_confidences
    ):

        top, right, bottom, left = (
            face_location
        )

        # Draw rectangle
        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )

        # Display confidence
        if confidence is not None:

            label = (
                f"Face: {confidence:.2f}"
            )

            cv2.putText(
                frame,
                label,
                (left, max(top - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

    return frame


# ============================================================
# SIMPLE CAMERA TEST
# ============================================================

def start_camera_test():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print(
            "Could not open camera."
        )

        return

    print(
        "YOLO face detection started."
    )

    print(
        "Press Q to quit."
    )

    while True:

        ret, frame = cap.read()

        if not ret:

            print(
                "Could not read camera frame."
            )

            break

        (
            face_locations,
            rgb_frame,
            yolo_confidences
        ) = detect_faces(frame)

        frame = draw_face_boxes(
            frame,
            face_locations,
            yolo_confidences
        )

        # Display number of faces
        cv2.putText(
            frame,
            f"Faces: {len(face_locations)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "YOLO Face Detection",
            frame
        )

        if (
            cv2.waitKey(1)
            & 0xFF
            == ord("q")
        ):
            break

    cap.release()

    cv2.destroyAllWindows()


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    start_camera_test()