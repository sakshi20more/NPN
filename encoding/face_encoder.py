import cv2
import face_recognition


def generate_embedding(frame, face_locations=None):
    """
    Generate a 128-dimensional face embedding.

    Args:
        frame:
            OpenCV BGR image/frame.

        face_locations:
            Optional face locations.
            If not provided, faces will be detected.

    Returns:
        128-dimensional numpy array if exactly one face
        is successfully encoded.

        None if:
        - no face is detected
        - multiple faces are detected
        - encoding fails
    """

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Detect faces if locations weren't provided
    if face_locations is None:

        face_locations = face_recognition.face_locations(
            rgb_frame
        )

    # We require exactly one face
    if len(face_locations) == 0:
        print("❌ No face detected.")
        return None

    if len(face_locations) > 1:
        print("❌ Multiple faces detected.")
        return None

    # Generate face encoding
    encodings = face_recognition.face_encodings(
        rgb_frame,
        face_locations
    )

    if not encodings:
        print("❌ Could not generate face encoding.")
        return None

    # face_recognition returns a 128-dimensional vector
    embedding = encodings[0]

    return embedding