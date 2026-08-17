# import cv2
# import face_recognition


# def detect_faces(frame):
#     """
#     Detect faces in an OpenCV frame.

#     Args:
#         frame: OpenCV BGR image.

#     Returns:
#         face_locations: List of detected face locations.
#         rgb_frame: RGB version of the frame.
#     """

#     # Convert OpenCV's BGR format to RGB
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # Detect faces
#     face_locations = face_recognition.face_locations(rgb_frame)

#     return face_locations, rgb_frame


# def get_face_encoding(frame):
#     """
#     Detect a single face and generate its 128-dimensional encoding.

#     Args:
#         frame: OpenCV BGR image.

#     Returns:
#         encoding: 128-dimensional face encoding.
#         None: If zero or multiple faces are detected.
#     """

#     face_locations, rgb_frame = detect_faces(frame)

#     # Enrollment requires exactly one face
#     if len(face_locations) != 1:
#         return None

#     encodings = face_recognition.face_encodings(
#         rgb_frame,
#         face_locations
#     )

#     if len(encodings) == 0:
#         return None

#     return encodings[0]


# def draw_face_boxes(frame, face_locations):
#     """
#     Draw rectangles around detected faces.

#     Args:
#         frame: OpenCV BGR image.
#         face_locations: Face locations returned by face_recognition.

#     Returns:
#         frame with face rectangles.
#     """

#     for top, right, bottom, left in face_locations:

#         cv2.rectangle(
#             frame,
#             (left, top),
#             (right, bottom),
#             (0, 255, 0),
#             2
#         )

#     return frame


# def start_camera_test():
#     """
#     Test webcam and face detection.
#     """

#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("❌ Camera could not be opened")
#         return

#     print("✅ Camera started")
#     print("Press Q to quit")

#     while True:

#         ret, frame = cap.read()

#         if not ret:
#             print("❌ Failed to read frame")
#             break

#         # Detect faces
#         face_locations, _ = detect_faces(frame)

#         # Draw face boxes
#         frame = draw_face_boxes(
#             frame,
#             face_locations
#         )

#         # Display number of faces
#         cv2.putText(
#             frame,
#             f"Faces detected: {len(face_locations)}",
#             (20, 40),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2
#         )

#         cv2.imshow(
#             "Face Detection",
#             frame
#         )

#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     cap.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     start_camera_test()

import cv2
import face_recognition


def detect_faces(frame):
    """
    Detect faces in an OpenCV BGR frame.

    Returns:
        face_locations: List of detected face locations
        rgb_frame: RGB version of the frame
    """

    # OpenCV captures images in BGR.
    # face_recognition expects RGB.
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    face_locations = face_recognition.face_locations(
        rgb_frame
    )

    return face_locations, rgb_frame


def draw_face_boxes(frame, face_locations):
    """
    Draw rectangles around detected faces.
    """

    for top, right, bottom, left in face_locations:

        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )

    return frame


def start_camera_test():
    """
    Simple standalone camera test for face detection.
    """

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Camera could not be opened")
        return

    print("✅ Camera started")
    print("Press Q to quit")

    while True:

        ret, frame = cap.read()

        if not ret:
            print("❌ Could not read camera frame")
            break

        face_locations, _ = detect_faces(frame)

        draw_face_boxes(
            frame,
            face_locations
        )

        cv2.putText(
            frame,
            f"Faces detected: {len(face_locations)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "Face Detection",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_camera_test()