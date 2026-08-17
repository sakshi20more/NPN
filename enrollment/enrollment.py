# import os
# import cv2
# import numpy as np

# from detection.face_detector import (
#     detect_faces,
#     draw_face_boxes
# )
# import face_recognition


# # Project root
# BASE_DIR = os.path.dirname(
#     os.path.dirname(os.path.abspath(__file__))
# )

# # Embeddings directory
# EMBEDDINGS_DIR = os.path.join(
#     BASE_DIR,
#     "data",
#     "embeddings"
# )


# def enroll_customer(customer_id):

#     os.makedirs(
#         EMBEDDINGS_DIR,
#         exist_ok=True
#     )

#     output_path = os.path.join(
#         EMBEDDINGS_DIR,
#         f"{customer_id}.npy"
#     )

#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("❌ Camera could not be opened")
#         return False

#     print("\n===================================")
#     print("       CUSTOMER ENROLLMENT")
#     print("===================================")
#     print(f"Customer ID: {customer_id}")
#     print()
#     print("Look directly at the camera.")
#     print("Press SPACE to capture.")
#     print("Press Q to cancel.\n")

#     while True:

#         ret, frame = cap.read()

#         if not ret:
#             print("❌ Failed to read camera frame")
#             break

#         # IMPORTANT:
#         # Detect faces using the ORIGINAL frame
#         face_locations, rgb_frame = detect_faces(frame)

#         # Draw boxes only for display
#         display_frame = frame.copy()

#         draw_face_boxes(
#             display_frame,
#             face_locations
#         )

#         cv2.putText(
#             display_frame,
#             f"Faces detected: {len(face_locations)}",
#             (20, 40),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.8,
#             (0, 255, 0),
#             2
#         )

#         cv2.imshow(
#             "Customer Enrollment",
#             display_frame
#         )

#         key = cv2.waitKey(1) & 0xFF

#         # SPACE = capture
#         if key == ord(" "):

#             if len(face_locations) == 0:
#                 print("❌ No face detected.")
#                 continue

#             if len(face_locations) > 1:
#                 print("❌ Multiple faces detected.")
#                 print("Please make sure only one person is visible.")
#                 continue

#             # Generate encoding from ORIGINAL RGB frame
#             encodings = face_recognition.face_encodings(
#                 rgb_frame,
#                 face_locations
#             )

#             if not encodings:
#                 print("❌ Could not generate face encoding.")
#                 print("Try moving closer to the camera.")
#                 continue

#             encoding = encodings[0]

#             # Save embedding
#             np.save(
#                 output_path,
#                 encoding
#             )

#             print("\n✅ Enrollment successful!")
#             print(f"Customer ID: {customer_id}")
#             print(f"Embedding saved at:")
#             print(output_path)
#             print(f"Embedding shape: {encoding.shape}")

#             break

#         # Q = cancel
#         elif key == ord("q"):

#             print("❌ Enrollment cancelled.")

#             cap.release()
#             cv2.destroyAllWindows()

#             return False

#     cap.release()
#     cv2.destroyAllWindows()

#     return True


# if __name__ == "__main__":

#     customer_id = input(
#         "Enter customer ID: "
#     ).strip()

#     if not customer_id:

#         print("❌ Customer ID cannot be empty.")

#     else:

#         enroll_customer(customer_id)

import os
import cv2
import numpy as np


from detection.face_detector import (
    detect_faces,
    draw_face_boxes
)

from encoding.face_encoder import (
    generate_embedding
)


# Get project root directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Temporary development storage
EMBEDDINGS_DIR = os.path.join(
    BASE_DIR,
    "data",
    "embeddings"
)


def enroll_customer(customer_id):

    # Create embeddings directory if it doesn't exist
    os.makedirs(
        EMBEDDINGS_DIR,
        exist_ok=True
    )

    output_path = os.path.join(
        EMBEDDINGS_DIR,
        f"{customer_id}.npy"
    )

    # Open webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print("❌ Camera could not be opened")
        return False

    print("\n===================================")
    print("       CUSTOMER ENROLLMENT")
    print("===================================")
    print(f"Customer ID: {customer_id}")
    print()
    print("Look directly at the camera.")
    print("Press SPACE to capture.")
    print("Press Q to cancel.\n")

    while True:

        ret, frame = cap.read()

        if not ret:

            print("❌ Failed to read camera frame")
            break

        # Detect faces
        face_locations, _, yolo_confidences = detect_faces(
            frame
        )

        # Create a separate frame for display
        display_frame = frame.copy()

        # Draw detection boxes only on display frame
        draw_face_boxes(
            display_frame,
            face_locations
        )

        # Display number of detected faces
        cv2.putText(
            display_frame,
            f"Faces detected: {len(face_locations)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "Customer Enrollment",
            display_frame
        )

        key = cv2.waitKey(1) & 0xFF

        # --------------------------------
        # SPACE → Capture face
        # --------------------------------

        if key == ord(" "):

            # No face
            if len(face_locations) == 0:

                print("❌ No face detected.")
                print("Please position your face properly.")
                continue

            # Multiple faces
            if len(face_locations) > 1:

                print("❌ Multiple faces detected.")
                print("Please make sure only one person is visible.")
                continue

            # Generate embedding from ORIGINAL frame
            embedding = generate_embedding(
                frame,
                face_locations
            )

            # Encoding failed
            if embedding is None:

                print("❌ Could not generate face encoding.")
                continue

            # Save embedding temporarily
            np.save(
                output_path,
                embedding
            )

            print("\n✅ Enrollment successful!")
            print(f"Customer ID: {customer_id}")
            print()
            print("Embedding saved at:")
            print(output_path)
            print()
            print(f"Embedding shape: {embedding.shape}")

            break

        # --------------------------------
        # Q → Cancel
        # --------------------------------

        elif key == ord("q"):

            print("❌ Enrollment cancelled.")

            cap.release()
            cv2.destroyAllWindows()

            return False

    cap.release()
    cv2.destroyAllWindows()

    return True


if __name__ == "__main__":

    customer_id = input(
        "Enter customer ID: "
    ).strip()

    if not customer_id:

        print("❌ Customer ID cannot be empty.")

    else:

        enroll_customer(
            customer_id
        )