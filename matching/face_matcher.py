import os

import cv2
import numpy as np
import face_recognition

from detection.face_detector import detect_faces
from encoding.face_encoder import generate_embedding
from liveness.liveness_detector import LivenessDetector


# ============================================================
# CONFIGURATION
# ============================================================

FACE_DISTANCE_THRESHOLD = 0.50

EMBEDDINGS_DIR = os.path.join(
    "data",
    "embeddings"
)

CAMERA_INDEX = 0


# ============================================================
# LOAD CUSTOMER EMBEDDING
# ============================================================

def load_customer_embedding(customer_id):
    """
    Load a customer's registered embedding.

    Current development storage:
        data/embeddings/<customer_id>.npy

    Later:
        Backend can retrieve this from PostgreSQL.
    """

    embedding_path = os.path.join(
        EMBEDDINGS_DIR,
        f"{customer_id}.npy"
    )

    if not os.path.exists(embedding_path):

        raise FileNotFoundError(
            f"No face embedding found for "
            f"customer: {customer_id}"
        )

    return np.load(embedding_path)


# ============================================================
# COMPARE EMBEDDINGS
# ============================================================

def compare_embeddings(
    live_embedding,
    stored_embedding,
    threshold=FACE_DISTANCE_THRESHOLD
):
    """
    Compare live and stored face embeddings.
    """

    live_embedding = np.asarray(
        live_embedding
    )

    stored_embedding = np.asarray(
        stored_embedding
    )

    if live_embedding.shape != stored_embedding.shape:

        raise ValueError(
            "Live and stored embeddings must "
            "have the same shape."
        )

    distance = face_recognition.face_distance(
        [stored_embedding],
        live_embedding
    )[0]

    verified = distance <= threshold

    return {
        "verified": bool(verified),
        "distance": float(distance),
        "threshold": float(threshold)
    }


# ============================================================
# LIVE CUSTOMER VERIFICATION
# ============================================================

def verify_customer(
    customer_id,
    threshold=FACE_DISTANCE_THRESHOLD
):
    """
    Complete face verification pipeline.

    Flow:

        Customer ID
             ↓
        Stored embedding
             ↓
        Camera
             ↓
        Liveness
             ↓
        Face detection
             ↓
        Face encoding
             ↓
        Face matching
             ↓
        Final result
    """

    # ========================================================
    # STEP 1: LOAD CUSTOMER EMBEDDING
    # ========================================================

    try:

        stored_embedding = load_customer_embedding(
            customer_id
        )

    except FileNotFoundError as e:

        print(f"\n❌ {e}")

        return {
            "customer_id": customer_id,
            "verified": False,
            "liveness": False,
            "distance": None,
            "threshold": threshold,
            "error": "Customer embedding not found"
        }

    print("\n===================================")
    print("       CUSTOMER VERIFICATION")
    print("===================================")

    print(
        f"Customer ID: {customer_id}"
    )

    print(
        "✅ Stored embedding loaded."
    )

    # ========================================================
    # STEP 2: CREATE LIVENESS DETECTOR
    # ========================================================

    liveness_detector = LivenessDetector()

    # ========================================================
    # STEP 3: OPEN CAMERA
    # ========================================================

    cap = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not cap.isOpened():

        print(
            "\n❌ Camera could not be opened."
        )

        return {
            "customer_id": customer_id,
            "verified": False,
            "liveness": False,
            "distance": None,
            "threshold": threshold,
            "error": "Camera could not be opened"
        }

    print("\nLook directly at the camera.")
    print("Please blink once.")
    print("Press Q to cancel.")

    # ========================================================
    # STATE
    # ========================================================

    liveness_passed = False
    verification_result = None

    # ========================================================
    # STEP 4: CAMERA LOOP
    # ========================================================

    while True:

        ret, frame = cap.read()

        if not ret:

            print(
                "\n❌ Could not read camera frame."
            )

            break

        display_frame = frame.copy()

        # ====================================================
        # STEP 4A: LIVENESS
        # ====================================================

        if not liveness_passed:

            liveness_passed = (
                liveness_detector.process_frame(
                    frame
                )
            )

            cv2.putText(
                display_frame,
                "Liveness: BLINK",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            if liveness_passed:

                print(
                    "\n✅ Liveness check passed."
                )

        else:

            cv2.putText(
                display_frame,
                "Liveness: PASSED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        # ====================================================
        # STEP 4B: FACE DETECTION
        # ====================================================

        face_locations, _ = detect_faces(
            frame
        )

        # Draw detected faces

        for top, right, bottom, left in face_locations:

            cv2.rectangle(
                display_frame,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )

        cv2.putText(
            display_frame,
            f"Faces: {len(face_locations)}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        # ====================================================
        # STEP 4C: AFTER LIVENESS PASSES
        # ====================================================

        if liveness_passed:

            # Exactly one face required

            if len(face_locations) == 1:

                # --------------------------------------------
                # Generate live embedding
                # --------------------------------------------

                live_embedding = generate_embedding(
                    frame,
                    face_locations
                )

                if live_embedding is not None:

                    print(
                        "✅ Live face embedding generated."
                    )

                    # ----------------------------------------
                    # Compare embeddings
                    # ----------------------------------------

                    verification_result = (
                        compare_embeddings(
                            live_embedding,
                            stored_embedding,
                            threshold
                        )
                    )

                    break

            elif len(face_locations) > 1:

                cv2.putText(
                    display_frame,
                    "Multiple faces detected",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

        # ====================================================
        # DISPLAY
        # ====================================================

        cv2.imshow(
            "Customer Verification",
            display_frame
        )

        # ====================================================
        # QUIT
        # ====================================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            print(
                "\n❌ Verification cancelled."
            )

            break

    # ========================================================
    # CLEANUP
    # ========================================================

    cap.release()
    cv2.destroyAllWindows()

    # ========================================================
    # IF VERIFICATION WAS NOT COMPLETED
    # ========================================================

    if verification_result is None:

        return {
            "customer_id": customer_id,
            "verified": False,
            "liveness": liveness_passed,
            "distance": None,
            "threshold": threshold,
            "error": "Verification cancelled or failed"
        }

    # ========================================================
    # FINAL RESULT
    # ========================================================

    result = {
        "customer_id": customer_id,
        "verified": verification_result["verified"],
        "liveness": liveness_passed,
        "distance": verification_result["distance"],
        "threshold": verification_result["threshold"]
    }

    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    print("\n===================================")
    print("       VERIFICATION RESULT")
    print("===================================")

    print(
        f"Customer ID : {result['customer_id']}"
    )

    print(
        f"Liveness    : {result['liveness']}"
    )

    print(
        f"Distance    : {result['distance']:.4f}"
    )

    print(
        f"Threshold   : {result['threshold']:.2f}"
    )

    if result["verified"]:

        print("\n✅ VERIFIED")

    else:

        print("\n❌ NOT VERIFIED")

    print(
        "==================================="
    )

    return result


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("\n===================================")
    print("     CUSTOMER FACE VERIFICATION")
    print("===================================")

    customer_id = input(
        "\nEnter Customer ID: "
    ).strip()

    if not customer_id:

        print(
            "\n❌ Customer ID cannot be empty."
        )

    else:

        verify_customer(
            customer_id
        )

# import os
# import cv2
# import numpy as np
# import face_recognition

# from detection.face_detector import detect_faces
# from encoding.face_encoder import generate_embedding


# # ============================================================
# # CONFIGURATION
# # ============================================================

# # Face distance must be <= this value to be considered a match.
# # Lower value = stricter matching.
# FACE_DISTANCE_THRESHOLD = 0.50

# # Temporary local storage.
# # Later, PostgreSQL will replace this.
# EMBEDDINGS_DIR = os.path.join(
#     "data",
#     "embeddings"
# )

# # Camera index.
# # 0 = default webcam.
# CAMERA_INDEX = 0


# # ============================================================
# # LOAD STORED CUSTOMER EMBEDDING
# # ============================================================

# def load_customer_embedding(customer_id):
#     """
#     Load the registered face embedding for a customer.

#     Currently:
#         Loads from data/embeddings/<customer_id>.npy

#     Future:
#         Backend can retrieve the embedding from PostgreSQL
#         and pass it directly to compare_embeddings().
#     """

#     embedding_path = os.path.join(
#         EMBEDDINGS_DIR,
#         f"{customer_id}.npy"
#     )

#     if not os.path.exists(embedding_path):
#         raise FileNotFoundError(
#             f"No face embedding found for customer: "
#             f"{customer_id}"
#         )

#     embedding = np.load(
#         embedding_path
#     )

#     return embedding


# # ============================================================
# # CORE MATCHING FUNCTION
# # ============================================================

# def compare_embeddings(
#     live_embedding,
#     stored_embedding,
#     threshold=FACE_DISTANCE_THRESHOLD
# ):
#     """
#     Compare a live face embedding with a customer's
#     stored face embedding.

#     Args:
#         live_embedding:
#             Embedding generated from the live camera image.

#         stored_embedding:
#             Registered customer's face embedding.

#         threshold:
#             Maximum allowed face distance.

#     Returns:
#         Dictionary containing:
#             verified
#             distance
#             threshold
#     """

#     live_embedding = np.asarray(
#         live_embedding
#     )

#     stored_embedding = np.asarray(
#         stored_embedding
#     )

#     # --------------------------------------------------------
#     # Validate embedding shape
#     # --------------------------------------------------------

#     if live_embedding.shape != stored_embedding.shape:
#         raise ValueError(
#             "Live and stored embeddings must have "
#             "the same shape."
#         )

#     # --------------------------------------------------------
#     # Calculate face distance
#     # --------------------------------------------------------

#     distance = face_recognition.face_distance(
#         [stored_embedding],
#         live_embedding
#     )[0]

#     # --------------------------------------------------------
#     # Decide match
#     # --------------------------------------------------------

#     verified = distance <= threshold

#     return {
#         "verified": bool(verified),
#         "distance": float(distance),
#         "threshold": float(threshold)
#     }


# # ============================================================
# # LIVE FACE VERIFICATION
# # ============================================================

# def verify_customer(
#     customer_id,
#     threshold=FACE_DISTANCE_THRESHOLD
# ):
#     """
#     Verify a customer using their live face.

#     Workflow:

#         Customer ID
#              ↓
#         Load stored embedding
#              ↓
#         Open camera
#              ↓
#         Detect face
#              ↓
#         Generate live embedding
#              ↓
#         Compare embeddings
#              ↓
#         VERIFIED / NOT VERIFIED

#     Returns:
#         Dictionary containing verification result.
#     """

#     # ========================================================
#     # STEP 1: LOAD CUSTOMER EMBEDDING
#     # ========================================================

#     try:

#         stored_embedding = load_customer_embedding(
#             customer_id
#         )

#     except FileNotFoundError as e:

#         print(f"\n❌ {e}")

#         return {
#             "verified": False,
#             "distance": None,
#             "threshold": threshold,
#             "customer_id": customer_id,
#             "error": "Customer embedding not found"
#         }

#     print("\n===================================")
#     print("       FACE VERIFICATION")
#     print("===================================")

#     print(
#         f"Customer ID: {customer_id}"
#     )

#     print(
#         "\n✅ Customer embedding loaded."
#     )

#     print(
#         f"Embedding shape: {stored_embedding.shape}"
#     )

#     print(
#         "\nLook at the camera."
#     )

#     print(
#         "Press SPACE to verify."
#     )

#     print(
#         "Press Q to cancel."
#     )

#     # ========================================================
#     # STEP 2: OPEN CAMERA
#     # ========================================================

#     cap = cv2.VideoCapture(
#         CAMERA_INDEX
#     )

#     if not cap.isOpened():

#         print(
#             "\n❌ Camera could not be opened."
#         )

#         return {
#             "verified": False,
#             "distance": None,
#             "threshold": threshold,
#             "customer_id": customer_id,
#             "error": "Camera could not be opened"
#         }

#     result = None

#     # ========================================================
#     # STEP 3: CAMERA LOOP
#     # ========================================================

#     while True:

#         ret, frame = cap.read()

#         if not ret:

#             print(
#                 "\n❌ Could not read camera frame."
#             )

#             break

#         # ----------------------------------------------------
#         # Detect faces using your existing detector
#         # ----------------------------------------------------

#         face_locations, _ = detect_faces(
#             frame
#         )

#         display_frame = frame.copy()

#         # ----------------------------------------------------
#         # Draw face boxes
#         # ----------------------------------------------------

#         for top, right, bottom, left in face_locations:

#             cv2.rectangle(
#                 display_frame,
#                 (left, top),
#                 (right, bottom),
#                 (0, 255, 0),
#                 2
#             )

#         # ----------------------------------------------------
#         # Display number of faces
#         # ----------------------------------------------------

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
#             "Face Verification",
#             display_frame
#         )

#         key = cv2.waitKey(1) & 0xFF

#         # ====================================================
#         # CANCEL
#         # ====================================================

#         if key == ord("q"):

#             print(
#                 "\n❌ Verification cancelled."
#             )

#             break

#         # ====================================================
#         # CAPTURE / VERIFY
#         # ====================================================

#         if key == ord(" "):

#             # ------------------------------------------------
#             # Check face count
#             # ------------------------------------------------

#             if len(face_locations) == 0:

#                 print(
#                     "\n❌ No face detected."
#                 )

#                 continue

#             if len(face_locations) > 1:

#                 print(
#                     "\n❌ Multiple faces detected."
#                 )

#                 print(
#                     "Please make sure only the customer "
#                     "is in front of the camera."
#                 )

#                 continue

#             print(
#                 "\n✅ Face detected."
#             )

#             # ------------------------------------------------
#             # Generate live embedding
#             # ------------------------------------------------

#             live_embedding = generate_embedding(
#                 frame,
#                 face_locations
#             )

#             if live_embedding is None:

#                 print(
#                     "❌ Could not generate face embedding."
#                 )

#                 continue

#             print(
#                 "✅ Live face embedding generated."
#             )

#             # ------------------------------------------------
#             # Compare live vs stored
#             # ------------------------------------------------

#             result = compare_embeddings(
#                 live_embedding,
#                 stored_embedding,
#                 threshold
#             )

#             # ------------------------------------------------
#             # Display result
#             # ------------------------------------------------

#             print(
#                 "\n==================================="
#             )

#             print(
#                 "       VERIFICATION RESULT"
#             )

#             print(
#                 "==================================="
#             )

#             print(
#                 f"Customer ID : {customer_id}"
#             )

#             print(
#                 f"Distance    : "
#                 f"{result['distance']:.4f}"
#             )

#             print(
#                 f"Threshold   : "
#                 f"{result['threshold']:.2f}"
#             )

#             if result["verified"]:

#                 print(
#                     "\n✅ VERIFIED"
#                 )

#             else:

#                 print(
#                     "\n❌ NOT VERIFIED"
#                 )

#             print(
#                 "==================================="
#             )

#             break

#     # ========================================================
#     # CLEANUP
#     # ========================================================

#     cap.release()
#     cv2.destroyAllWindows()

#     # ========================================================
#     # RETURN RESULT
#     # ========================================================

#     if result is None:

#         return {
#             "verified": False,
#             "distance": None,
#             "threshold": threshold,
#             "customer_id": customer_id,
#             "error": "Verification cancelled or failed"
#         }

#     result["customer_id"] = customer_id

#     return result


# # ============================================================
# # LOCAL TEST
# # ============================================================

# if __name__ == "__main__":

#     print("\n===================================")
#     print("     CUSTOMER FACE VERIFICATION")
#     print("===================================")

#     customer_id = input(
#         "\nEnter Customer ID: "
#     ).strip()

#     if not customer_id:

#         print(
#             "\n❌ Customer ID cannot be empty."
#         )

#     else:

#         result = verify_customer(
#             customer_id
#         )

#         print("\nFinal Result:")

#         print(
#             f"Customer ID: "
#             f"{result['customer_id']}"
#         )

#         print(
#             f"Verified: "
#             f"{result['verified']}"
#         )

#         if result["distance"] is not None:

#             print(
#                 f"Distance: "
#                 f"{result['distance']:.4f}"
#             )

#         print(
#             f"Threshold: "
#             f"{result['threshold']}"
#         )