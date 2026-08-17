# import os

# import cv2
# import numpy as np
# import face_recognition

# from detection.face_detector import detect_faces
# from encoding.face_encoder import generate_embedding
# from liveness.liveness_detector import LivenessDetector


# # ============================================================
# # CONFIGURATION
# # ============================================================

# FACE_DISTANCE_THRESHOLD = 0.50

# EMBEDDINGS_DIR = os.path.join(
#     "data",
#     "embeddings"
# )

# CAMERA_INDEX = 0


# # ============================================================
# # LOAD CUSTOMER EMBEDDING
# # ============================================================

# def load_customer_embedding(customer_id):
#     """
#     Load a customer's registered embedding.

#     Current development storage:
#         data/embeddings/<customer_id>.npy

#     Later:
#         Backend can retrieve this from PostgreSQL.
#     """

#     embedding_path = os.path.join(
#         EMBEDDINGS_DIR,
#         f"{customer_id}.npy"
#     )

#     if not os.path.exists(embedding_path):

#         raise FileNotFoundError(
#             f"No face embedding found for "
#             f"customer: {customer_id}"
#         )

#     return np.load(embedding_path)


# # ============================================================
# # COMPARE EMBEDDINGS
# # ============================================================

# def compare_embeddings(
#     live_embedding,
#     stored_embedding,
#     threshold=FACE_DISTANCE_THRESHOLD
# ):
#     """
#     Compare live and stored face embeddings.
#     """

#     live_embedding = np.asarray(
#         live_embedding
#     )

#     stored_embedding = np.asarray(
#         stored_embedding
#     )

#     if live_embedding.shape != stored_embedding.shape:

#         raise ValueError(
#             "Live and stored embeddings must "
#             "have the same shape."
#         )

#     distance = face_recognition.face_distance(
#         [stored_embedding],
#         live_embedding
#     )[0]

#     verified = distance <= threshold

#     return {
#         "verified": bool(verified),
#         "distance": float(distance),
#         "threshold": float(threshold)
#     }


# # ============================================================
# # LIVE CUSTOMER VERIFICATION
# # ============================================================

# def verify_customer(
#     customer_id,
#     threshold=FACE_DISTANCE_THRESHOLD
# ):
#     """
#     Complete face verification pipeline.

#     Flow:

#         Customer ID
#              ↓
#         Stored embedding
#              ↓
#         Camera
#              ↓
#         Liveness
#              ↓
#         Face detection
#              ↓
#         Face encoding
#              ↓
#         Face matching
#              ↓
#         Final result
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
#             "customer_id": customer_id,
#             "verified": False,
#             "liveness": False,
#             "distance": None,
#             "threshold": threshold,
#             "error": "Customer embedding not found"
#         }

#     print("\n===================================")
#     print("       CUSTOMER VERIFICATION")
#     print("===================================")

#     print(
#         f"Customer ID: {customer_id}"
#     )

#     print(
#         "✅ Stored embedding loaded."
#     )

#     # ========================================================
#     # STEP 2: CREATE LIVENESS DETECTOR
#     # ========================================================

#     liveness_detector = LivenessDetector()

#     # ========================================================
#     # STEP 3: OPEN CAMERA
#     # ========================================================

#     cap = cv2.VideoCapture(
#         CAMERA_INDEX
#     )

#     if not cap.isOpened():

#         print(
#             "\n❌ Camera could not be opened."
#         )

#         return {
#             "customer_id": customer_id,
#             "verified": False,
#             "liveness": False,
#             "distance": None,
#             "threshold": threshold,
#             "error": "Camera could not be opened"
#         }

#     print("\nLook directly at the camera.")
#     print("Please blink once.")
#     print("Press Q to cancel.")

#     # ========================================================
#     # STATE
#     # ========================================================

#     liveness_passed = False
#     verification_result = None

#     # ========================================================
#     # STEP 4: CAMERA LOOP
#     # ========================================================

#     while True:

#         ret, frame = cap.read()

#         if not ret:

#             print(
#                 "\n❌ Could not read camera frame."
#             )

#             break

#         display_frame = frame.copy()

#         # ====================================================
#         # STEP 4A: LIVENESS
#         # ====================================================

#         if not liveness_passed:

#             liveness_passed = (
#                 liveness_detector.process_frame(
#                     frame
#                 )
#             )

#             cv2.putText(
#                 display_frame,
#                 "Liveness: BLINK",
#                 (20, 40),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.8,
#                 (0, 255, 255),
#                 2
#             )

#             if liveness_passed:

#                 print(
#                     "\n✅ Liveness check passed."
#                 )

#         else:

#             cv2.putText(
#                 display_frame,
#                 "Liveness: PASSED",
#                 (20, 40),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.8,
#                 (0, 255, 0),
#                 2
#             )

#         # ====================================================
#         # STEP 4B: FACE DETECTION
#         # ====================================================

#         face_locations, _ = detect_faces(
#             frame
#         )

#         # Draw detected faces

#         for top, right, bottom, left in face_locations:

#             cv2.rectangle(
#                 display_frame,
#                 (left, top),
#                 (right, bottom),
#                 (0, 255, 0),
#                 2
#             )

#         cv2.putText(
#             display_frame,
#             f"Faces: {len(face_locations)}",
#             (20, 80),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.8,
#             (0, 255, 0),
#             2
#         )

#         # ====================================================
#         # STEP 4C: AFTER LIVENESS PASSES
#         # ====================================================

#         if liveness_passed:

#             # Exactly one face required

#             if len(face_locations) == 1:

#                 # --------------------------------------------
#                 # Generate live embedding
#                 # --------------------------------------------

#                 live_embedding = generate_embedding(
#                     frame,
#                     face_locations
#                 )

#                 if live_embedding is not None:

#                     print(
#                         "✅ Live face embedding generated."
#                     )

#                     # ----------------------------------------
#                     # Compare embeddings
#                     # ----------------------------------------

#                     verification_result = (
#                         compare_embeddings(
#                             live_embedding,
#                             stored_embedding,
#                             threshold
#                         )
#                     )

#                     break

#             elif len(face_locations) > 1:

#                 cv2.putText(
#                     display_frame,
#                     "Multiple faces detected",
#                     (20, 120),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7,
#                     (0, 0, 255),
#                     2
#                 )

#         # ====================================================
#         # DISPLAY
#         # ====================================================

#         cv2.imshow(
#             "Customer Verification",
#             display_frame
#         )

#         # ====================================================
#         # QUIT
#         # ====================================================

#         key = cv2.waitKey(1) & 0xFF

#         if key == ord("q"):

#             print(
#                 "\n❌ Verification cancelled."
#             )

#             break

#     # ========================================================
#     # CLEANUP
#     # ========================================================

#     cap.release()
#     cv2.destroyAllWindows()

#     # ========================================================
#     # IF VERIFICATION WAS NOT COMPLETED
#     # ========================================================

#     if verification_result is None:

#         return {
#             "customer_id": customer_id,
#             "verified": False,
#             "liveness": liveness_passed,
#             "distance": None,
#             "threshold": threshold,
#             "error": "Verification cancelled or failed"
#         }

#     # ========================================================
#     # FINAL RESULT
#     # ========================================================

#     result = {
#         "customer_id": customer_id,
#         "verified": verification_result["verified"],
#         "liveness": liveness_passed,
#         "distance": verification_result["distance"],
#         "threshold": verification_result["threshold"]
#     }

#     # ========================================================
#     # DISPLAY RESULT
#     # ========================================================

#     print("\n===================================")
#     print("       VERIFICATION RESULT")
#     print("===================================")

#     print(
#         f"Customer ID : {result['customer_id']}"
#     )

#     print(
#         f"Liveness    : {result['liveness']}"
#     )

#     print(
#         f"Distance    : {result['distance']:.4f}"
#     )

#     print(
#         f"Threshold   : {result['threshold']:.2f}"
#     )

#     if result["verified"]:

#         print("\n✅ VERIFIED")

#     else:

#         print("\n❌ NOT VERIFIED")

#     print(
#         "==================================="
#     )

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

#         verify_customer(
#             customer_id
#         )

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

# import cv2
# import numpy as np
# import face_recognition

# from liveness.liveness_detector import LivenessDetector


# # ============================================================
# # CONFIGURATION
# # ============================================================

# FACE_DISTANCE_THRESHOLD = 0.50

# CAMERA_INDEX = 0


# # ============================================================
# # LOAD STORED EMBEDDING
# # ============================================================

# def load_embedding(path):
#     """
#     Load a customer's registered face embedding.

#     DEVELOPMENT ONLY.

#     Currently:
#         .npy file -> embedding

#     Later:
#         PostgreSQL -> backend -> embedding
#     """

#     embedding = np.load(path)

#     return np.asarray(
#         embedding,
#         dtype=np.float64
#     )


# # ============================================================
# # CAPTURE LIVE FACE + LIVENESS
# # ============================================================

# def capture_live_embedding(
#     camera_index=CAMERA_INDEX,
#     show_window=True
# ):
#     """
#     Open camera and perform liveness verification.

#     Liveness sequence:

#         1. BLINK
#         2. HEAD UP
#         3. HEAD DOWN

#     Only after successful liveness is a
#     live face embedding generated.

#     Returns:
#         {
#             "success": bool,
#             "liveness": dict,
#             "embedding": np.ndarray or None,
#             "reason": str
#         }
#     """

#     liveness_detector = LivenessDetector()

#     cap = cv2.VideoCapture(camera_index)

#     if not cap.isOpened():

#         return {
#             "success": False,
#             "liveness": {
#                 "live": False,
#                 "stage": "CAMERA_ERROR",
#                 "reason": "Camera could not be opened.",
#                 "face_count": 0
#             },
#             "embedding": None,
#             "reason": "Camera could not be opened."
#         }

#     print()
#     print("===================================")
#     print("       LIVENESS / ANTI-SPOOF")
#     print("===================================")
#     print()
#     print("Follow these instructions:")
#     print()
#     print("  1. BLINK once")
#     print("  2. Move your head UP")
#     print("  3. Move your head DOWN")
#     print()
#     print("Press Q to cancel.")
#     print()

#     # Used to print instructions only when
#     # the liveness stage changes.
#     previous_stage = None

#     final_liveness_result = None

#     try:

#         while True:

#             ret, frame = cap.read()

#             if not ret:

#                 final_liveness_result = {
#                     "live": False,
#                     "stage": "CAMERA_ERROR",
#                     "reason": "Could not read camera frame.",
#                     "face_count": 0
#                 }

#                 break

#             # =================================================
#             # PROCESS LIVENESS
#             # =================================================

#             liveness_result = (
#                 liveness_detector.process_frame(
#                     frame
#                 )
#             )

#             final_liveness_result = liveness_result

#             current_stage = (
#                 liveness_result["stage"]
#             )

#             # =================================================
#             # PRINT NEW INSTRUCTION
#             # =================================================

#             if current_stage != previous_stage:

#                 print()
#                 print(
#                     f"➡ {liveness_result['reason']}"
#                 )

#                 previous_stage = current_stage

#             # =================================================
#             # DISPLAY CAMERA WINDOW
#             # =================================================

#             if show_window:

#                 # Instruction
#                 cv2.putText(
#                     frame,
#                     liveness_result["reason"],
#                     (20, 40),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.60,
#                     (0, 255, 0),
#                     2
#                 )

#                 # Stage
#                 cv2.putText(
#                     frame,
#                     f"Stage: {liveness_result['stage']}",
#                     (20, 80),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.65,
#                     (255, 255, 0),
#                     2
#                 )

#                 # Live status
#                 cv2.putText(
#                     frame,
#                     f"Live: {liveness_result['live']}",
#                     (20, 120),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.65,
#                     (0, 255, 0),
#                     2
#                 )

#                 cv2.imshow(
#                     "Face Verification",
#                     frame
#                 )

#             # =================================================
#             # LIVENESS PASSED
#             # =================================================

#             if liveness_result["live"]:

#                 print()
#                 print(
#                     "==================================="
#                 )
#                 print(
#                     "       LIVENESS PASSED"
#                 )
#                 print(
#                     "==================================="
#                 )
#                 print(
#                     "✅ Blink detected"
#                 )
#                 print(
#                     "✅ Head UP detected"
#                 )
#                 print(
#                     "✅ Head DOWN detected"
#                 )

#                 break

#             # =================================================
#             # USER CANCEL
#             # =================================================

#             if show_window:

#                 key = cv2.waitKey(1) & 0xFF

#                 if key == ord("q"):

#                     final_liveness_result = {
#                         **liveness_result,
#                         "live": False,
#                         "stage": "CANCELLED",
#                         "reason": (
#                             "User cancelled verification."
#                         )
#                     }

#                     print()
#                     print(
#                         "❌ Verification cancelled."
#                     )

#                     break

#         # =====================================================
#         # LIVENESS FAILED / CANCELLED
#         # =====================================================

#         if not final_liveness_result["live"]:

#             return {
#                 "success": False,
#                 "liveness": final_liveness_result,
#                 "embedding": None,
#                 "reason": final_liveness_result["reason"]
#             }

#         # =====================================================
#         # CAPTURE FINAL FRAME
#         # =====================================================

#         ret, final_frame = cap.read()

#         if not ret:

#             return {
#                 "success": False,
#                 "liveness": final_liveness_result,
#                 "embedding": None,
#                 "reason": (
#                     "Could not capture "
#                     "final face frame."
#                 )
#             }

#         # =====================================================
#         # BGR → RGB
#         # =====================================================

#         rgb_frame = cv2.cvtColor(
#             final_frame,
#             cv2.COLOR_BGR2RGB
#         )

#         # =====================================================
#         # DETECT FACE
#         # =====================================================

#         face_locations = (
#             face_recognition.face_locations(
#                 rgb_frame
#             )
#         )

#         if len(face_locations) == 0:

#             return {
#                 "success": False,
#                 "liveness": final_liveness_result,
#                 "embedding": None,
#                 "reason": (
#                     "No face found after "
#                     "liveness verification."
#                 )
#             }

#         if len(face_locations) > 1:

#             return {
#                 "success": False,
#                 "liveness": final_liveness_result,
#                 "embedding": None,
#                 "reason": (
#                     "Multiple faces found."
#                 )
#             }

#         # =====================================================
#         # GENERATE LIVE EMBEDDING
#         # =====================================================

#         encodings = (
#             face_recognition.face_encodings(
#                 rgb_frame,
#                 face_locations
#             )
#         )

#         if len(encodings) == 0:

#             return {
#                 "success": False,
#                 "liveness": final_liveness_result,
#                 "embedding": None,
#                 "reason": (
#                     "Could not generate "
#                     "face embedding."
#                 )
#             }

#         live_embedding = encodings[0]

#         print()
#         print(
#             "✅ Live face embedding generated."
#         )

#         return {
#             "success": True,
#             "liveness": final_liveness_result,
#             "embedding": live_embedding,
#             "reason": (
#                 "Live face embedding generated."
#             )
#         }

#     finally:

#         cap.release()

#         if show_window:

#             cv2.destroyAllWindows()


# # ============================================================
# # COMPARE EMBEDDINGS
# # ============================================================

# def compare_embeddings(
#     live_embedding,
#     stored_embedding,
#     threshold=FACE_DISTANCE_THRESHOLD
# ):
#     """
#     Compare the live face embedding with the
#     registered customer's embedding.

#     This function is independent of:

#         Flask
#         FastAPI
#         PostgreSQL
#         Frontend
#     """

#     live_embedding = np.asarray(
#         live_embedding,
#         dtype=np.float64
#     )

#     stored_embedding = np.asarray(
#         stored_embedding,
#         dtype=np.float64
#     )

#     # --------------------------------------------------------
#     # Validate shape
#     # --------------------------------------------------------

#     if live_embedding.shape != stored_embedding.shape:

#         raise ValueError(
#             "Live and stored embeddings "
#             "must have the same shape."
#         )

#     # --------------------------------------------------------
#     # Calculate face distance
#     # --------------------------------------------------------

#     distance = face_recognition.face_distance(
#         [stored_embedding],
#         live_embedding
#     )[0]

#     # --------------------------------------------------------
#     # Verification
#     # --------------------------------------------------------

#     verified = (
#         distance <= threshold
#     )

#     return {
#         "verified": bool(verified),
#         "distance": float(distance),
#         "threshold": float(threshold)
#     }


# # ============================================================
# # COMPLETE CUSTOMER VERIFICATION
# # ============================================================

# def verify_customer(
#     customer_id,
#     stored_embedding,
#     threshold=FACE_DISTANCE_THRESHOLD,
#     camera_index=CAMERA_INDEX,
#     show_window=True
# ):
#     """
#     Complete face verification pipeline.

#     Parameters
#     ----------
#     customer_id:
#         Customer being verified.

#     stored_embedding:
#         Registered face embedding of that customer.

#         Currently:
#             loaded from .npy

#         Later:
#             retrieved from PostgreSQL.

#     threshold:
#         Face distance threshold.

#     camera_index:
#         Camera index.

#     show_window:
#         Whether to display camera window.

#     Returns
#     -------
#     dict
#         JSON-friendly verification result.
#     """

#     # ========================================================
#     # STEP 1
#     # LIVENESS + LIVE EMBEDDING
#     # ========================================================

#     live_result = capture_live_embedding(
#         camera_index=camera_index,
#         show_window=show_window
#     )

#     # ========================================================
#     # LIVENESS FAILED
#     # ========================================================

#     if not live_result["success"]:

#         return {
#             "customer_id": customer_id,
#             "verified": False,
#             "liveness": live_result["liveness"],
#             "distance": None,
#             "threshold": float(threshold),
#             "reason": live_result["reason"]
#         }

#     # ========================================================
#     # STEP 2
#     # FACE MATCHING
#     # ========================================================

#     live_embedding = (
#         live_result["embedding"]
#     )

#     match_result = compare_embeddings(
#         live_embedding,
#         stored_embedding,
#         threshold
#     )

#     # ========================================================
#     # FINAL RESULT
#     # ========================================================

#     if match_result["verified"]:

#         reason = "Face verified."

#     else:

#         reason = "Face does not match."

#     return {
#         "customer_id": customer_id,
#         "verified": match_result["verified"],
#         "liveness": live_result["liveness"],
#         "distance": match_result["distance"],
#         "threshold": match_result["threshold"],
#         "reason": reason
#     }


# # ============================================================
# # DEVELOPMENT / LOCAL TEST
# # ============================================================

# if __name__ == "__main__":

#     print()
#     print("===================================")
#     print("       FACE VERIFICATION")
#     print("===================================")
#     print()

#     # --------------------------------------------------------
#     # ASK FOR CUSTOMER ID
#     # --------------------------------------------------------

#     customer_id = input(
#         "Enter Customer ID: "
#     ).strip()

#     if not customer_id:

#         print(
#             "❌ Customer ID cannot be empty."
#         )

#         raise SystemExit

#     print()
#     print(
#         f"Customer selected: {customer_id}"
#     )

#     # --------------------------------------------------------
#     # DEVELOPMENT STORAGE
#     # --------------------------------------------------------
#     #
#     # Current:
#     #     data/embeddings/customer001.npy
#     #
#     # Future:
#     #     PostgreSQL → customer_id → embedding
#     #
#     # --------------------------------------------------------

#     stored_embedding_path = (
#         f"data/embeddings/{customer_id}.npy"
#     )

#     print(
#         f"Loading embedding from:"
#     )

#     print(
#         f"  {stored_embedding_path}"
#     )

#     # --------------------------------------------------------
#     # LOAD EMBEDDING
#     # --------------------------------------------------------

#     try:

#         stored_embedding = load_embedding(
#             stored_embedding_path
#         )

#     except FileNotFoundError:

#         print()
#         print(
#             "❌ Customer embedding not found."
#         )

#         print(
#             f"Expected file:"
#         )

#         print(
#             f"  {stored_embedding_path}"
#         )

#         raise SystemExit

#     except Exception as e:

#         print()
#         print(
#             f"❌ Could not load embedding: {e}"
#         )

#         raise SystemExit

#     # --------------------------------------------------------
#     # VALIDATE EMBEDDING
#     # --------------------------------------------------------

#     if stored_embedding.shape != (128,):

#         print()
#         print(
#             "❌ Invalid face embedding."
#         )

#         print(
#             f"Expected shape: (128,)"
#         )

#         print(
#             f"Received shape: {stored_embedding.shape}"
#         )

#         raise SystemExit

#     print()
#     print(
#         f"✅ Customer embedding loaded: "
#         f"{stored_embedding.shape}"
#     )

#     # ========================================================
#     # START VERIFICATION
#     # ========================================================

#     result = verify_customer(
#         customer_id=customer_id,
#         stored_embedding=stored_embedding,
#         threshold=FACE_DISTANCE_THRESHOLD,
#         camera_index=CAMERA_INDEX,
#         show_window=True
#     )

#     # ========================================================
#     # DISPLAY RESULT
#     # ========================================================

#     print()
#     print("===================================")
#     print("       VERIFICATION RESULT")
#     print("===================================")

#     print(
#         f"Customer ID : "
#         f"{result['customer_id']}"
#     )

#     print(
#         f"Liveness    : "
#         f"{result['liveness']}"
#     )

#     print(
#         f"Distance    : "
#         f"{result['distance']}"
#     )

#     print(
#         f"Threshold   : "
#         f"{result['threshold']}"
#     )

#     print(
#         f"Verified    : "
#         f"{result['verified']}"
#     )

#     print(
#         f"Reason      : "
#         f"{result['reason']}"
#     )

#     print("===================================")

import cv2
import numpy as np
import face_recognition
from risk.risk_predictor import calculate_risk 
from detection.face_detector import detect_faces
import time
import json


from liveness.liveness_detector import (
    LivenessDetector,
    draw_liveness_instruction
)


# ============================================================
# CONFIGURATION
# ============================================================

FACE_DISTANCE_THRESHOLD = 0.50

CAMERA_INDEX = 0


# ============================================================
# LOAD STORED EMBEDDING
# ============================================================

def load_embedding(path):
    """
    Development helper.

    Current:
        .npy file → embedding

    Future:
        PostgreSQL → backend → embedding
    """

    embedding = np.load(path)

    embedding = np.asarray(
        embedding,
        dtype=np.float64
    )

    return embedding


# ============================================================
# GENERATE EMBEDDING FROM FRAME
# ============================================================

def generate_embedding_from_frame(
    frame,
    face_locations=None
):
    """
    Generate a 128-dimensional face embedding
    from a camera frame.

    Args:
        frame:
            OpenCV BGR camera frame.

        face_locations:
            Face locations detected by YOLO.
            If None, face_recognition will detect
            the face as a fallback.

    Returns:
        embedding, reason
    """

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------------
    # FACE DETECTION
    # --------------------------------------------------------

    # Use YOLO locations when provided.
    # Otherwise use face_recognition as fallback.
    if face_locations is None:

        face_locations = (
            face_recognition.face_locations(
                rgb_frame
            )
        )

    # --------------------------------------------------------
    # NO FACE
    # --------------------------------------------------------

    if len(face_locations) == 0:

        return None, (
            "No face detected."
        )

    # --------------------------------------------------------
    # MULTIPLE FACES
    # --------------------------------------------------------

    if len(face_locations) > 1:

        return None, (
            "Multiple faces detected."
        )

    # --------------------------------------------------------
    # GENERATE EMBEDDING
    # --------------------------------------------------------

    encodings = (
        face_recognition.face_encodings(
            rgb_frame,
            known_face_locations=face_locations
        )
    )

    # --------------------------------------------------------
    # ENCODING FAILED
    # --------------------------------------------------------

    if len(encodings) == 0:

        return None, (
            "Could not generate face embedding."
        )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return encodings[0], (
        "Face embedding generated."
    )
# ============================================================
# CAPTURE LIVE FACE + LIVENESS
# ============================================================

def capture_live_embedding(
    camera_index=CAMERA_INDEX,
    show_window=True
):
    """
    Open camera and perform:

        BLINK
          ↓
        HEAD UP
          ↓
        HEAD DOWN
          ↓
        Generate embedding

    IMPORTANT:
    The final valid camera frame from the liveness
    process is used for face embedding generation.
    """

    detector = LivenessDetector()

    cap = cv2.VideoCapture(
        camera_index
    )

    if not cap.isOpened():

        return {
            "success": False,
            "liveness": {
                "live": False,
                "stage": "CAMERA_ERROR",
                "reason": (
                    "Camera could not be opened."
                ),
                "face_count": 0
            },
            "embedding": None,
            "reason": (
                "Camera could not be opened."
            )
        }

    print()
    print("===================================")
    print("       LIVENESS / ANTI-SPOOF")
    print("===================================")
    print()
    print("PLEASE FOLLOW THE CAMERA INSTRUCTIONS")
    print()
    print("1. BLINK ONCE")
    print("2. MOVE YOUR HEAD UP")
    print("3. MOVE YOUR HEAD DOWN")
    print()
    print("Press Q to cancel.")
    print()

    previous_stage = None

    # --------------------------------------------------------
    # IMPORTANT:
    # Keep the last valid frame.
    # --------------------------------------------------------

    last_valid_frame = None

    final_liveness_result = None

    try:

        while True:

            ret, frame = cap.read()

            if not ret:

                final_liveness_result = {
                    "live": False,
                    "stage": "CAMERA_ERROR",
                    "reason": (
                        "Could not read camera frame."
                    ),
                    "face_count": 0
                }

                break

            # ------------------------------------------------
            # Save the current frame
            # ------------------------------------------------

            last_valid_frame = frame.copy()

            # ------------------------------------------------
            # Process liveness
            # ------------------------------------------------

            result = detector.process_frame(
                frame
            )

            final_liveness_result = result

            # ------------------------------------------------
            # Print instruction when stage changes
            # ------------------------------------------------

            if (
                result["stage"]
                != previous_stage
            ):

                print()

                print(
                    "➡ "
                    + result["reason"].replace(
                        "\n",
                        " "
                    )
                )

                previous_stage = (
                    result["stage"]
                )

            # ------------------------------------------------
            # Draw UI
            # ------------------------------------------------

            if show_window:

                display_frame = (
                    draw_liveness_instruction(
                        frame.copy(),
                        result
                    )
                )

                cv2.imshow(
                    "Face Verification",
                    display_frame
                )

            # ------------------------------------------------
            # LIVENESS PASSED
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
                    "✅ BLINK completed"
                )
                print(
                    "✅ HEAD UP completed"
                )
                print(
                    "✅ HEAD DOWN completed"
                )

                break

            # ------------------------------------------------
            # USER CANCEL
            # ------------------------------------------------

            if show_window:

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key == ord("q"):

                    final_liveness_result = {
                        **result,
                        "live": False,
                        "stage": "CANCELLED",
                        "reason": (
                            "User cancelled verification."
                        )
                    }

                    print()
                    print(
                        "❌ Verification cancelled."
                    )

                    break

        # ====================================================
        # LIVENESS FAILED
        # ====================================================

        if (
            final_liveness_result is None
            or not final_liveness_result["live"]
        ):

            return {
                "success": False,
                "liveness": (
                    final_liveness_result
                ),
                "embedding": None,
                "reason": (
                    final_liveness_result[
                        "reason"
                    ]
                    if final_liveness_result
                    else "Liveness failed."
                )
            }

        # ====================================================
        # MAKE SURE WE HAVE A FRAME
        # ====================================================

        if last_valid_frame is None:

            return {
                "success": False,
                "liveness": final_liveness_result,
                "embedding": None,
                "reason": (
                    "No valid camera frame available."
                )
            }

        # ====================================================
        # GENERATE EMBEDDING
        # ====================================================

        print()
        print(
            "Generating live face embedding..."
        )

       # ========================================================
# YOLO FACE DETECTION
# ========================================================

        print()
        print("Detecting face with YOLO...")

        (
            face_locations,
            _,
            yolo_confidences
        ) = detect_faces(
            last_valid_frame
        )

        face_count = len(face_locations)

        print(
            f"Faces detected by YOLO: {face_count}"
        )

        # --------------------------------------------------------
        # No face
        # --------------------------------------------------------

        if face_count == 0:

            return {
                "success": False,
                "liveness": final_liveness_result,
                "embedding": None,
                "yolo_confidence": 0.0,
                "face_count": 0,
                "reason": "No face detected by YOLO."
            }

        # --------------------------------------------------------
        # Multiple faces
        # --------------------------------------------------------

        if face_count > 1:

            return {
                "success": False,
                "liveness": final_liveness_result,
                "embedding": None,
                "yolo_confidence": max(
                    yolo_confidences
                ),
                "face_count": face_count,
                "reason": "Multiple faces detected."
            }

    # --------------------------------------------------------
    # One face
    # --------------------------------------------------------

        yolo_confidence = float(
            yolo_confidences[0]
        )

        print(
            f"YOLO confidence: {yolo_confidence:.2f}"
        )

    # ========================================================
    # GENERATE EMBEDDING
    # ========================================================

      # ========================================================
# GENERATE EMBEDDING
# ========================================================

        print()
        print(
            "Generating live face embedding..."
        )

        face_count = len(face_locations)

        live_embedding, embedding_reason = (
            generate_embedding_from_frame(
                last_valid_frame,
                face_locations=face_locations
            )
        )

        # --------------------------------------------------------
        # Embedding failed
        # --------------------------------------------------------

        if live_embedding is None:

            return {
                "success": False,
                "liveness": final_liveness_result,
                "embedding": None,
                "face_count": face_count,
                "yolo_confidence": yolo_confidence,
                "reason": embedding_reason
            }

        print(
            "✅ Live face embedding generated."
        )

        return {
            "success": True,
            "liveness": final_liveness_result,
            "embedding": live_embedding,
            "face_count": face_count,
            "yolo_confidence": yolo_confidence,
            "reason": (
                "Live face embedding generated."
            )
        }

    finally:

        cap.release()

        if show_window:

            cv2.destroyAllWindows()


# ============================================================
# COMPARE EMBEDDINGS
# ============================================================

def compare_embeddings(
    live_embedding,
    stored_embedding,
    threshold=FACE_DISTANCE_THRESHOLD
):
    """
    Compare live embedding with the
    selected customer's stored embedding.
    """

    live_embedding = np.asarray(
        live_embedding,
        dtype=np.float64
    )

    stored_embedding = np.asarray(
        stored_embedding,
        dtype=np.float64
    )

    # --------------------------------------------------------
    # Validate dimensions
    # --------------------------------------------------------

    if live_embedding.shape != stored_embedding.shape:

        raise ValueError(
            "Live and stored embeddings "
            "must have the same shape."
        )

    # --------------------------------------------------------
    # Calculate distance
    # --------------------------------------------------------

    distance = face_recognition.face_distance(
        [stored_embedding],
        live_embedding
    )[0]

    verified = (
        distance <= threshold
    )

    return {
        "verified": bool(verified),
        "distance": float(distance),
        "threshold": float(threshold)
    }


# ============================================================
# COMPLETE VERIFICATION
# ============================================================
def verify_customer(
    customer_id,
    stored_embedding,
    threshold=FACE_DISTANCE_THRESHOLD,
    camera_index=CAMERA_INDEX,
    show_window=True
):
    """
    Complete face verification.

    Final result contains only:
        face_match
        face_confidence
        liveness_passed
        liveness_confidence
        spoof_probability
        processing_time_ms
    """

    # ========================================================
    # START TIMER
    # ========================================================

    start_time = time.perf_counter()

    # ========================================================
    # STEP 1
    # LIVENESS
    # ========================================================

    live_result = capture_live_embedding(
        camera_index=camera_index,
        show_window=show_window
    )

    # ========================================================
    # LIVENESS FAILED
    # ========================================================

    if not live_result["success"]:

        processing_time_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        return {
            "face_match": False,
            "face_confidence": 0.0,
            "liveness_passed": False,
            "liveness_confidence": 0.0,
            "spoof_probability": 1.0,
            "processing_time_ms": processing_time_ms
        }

    # ========================================================
    # STEP 2
    # FACE MATCHING
    # ========================================================

    live_embedding = (
        live_result["embedding"]
    )

    match_result = compare_embeddings(
        live_embedding,
        stored_embedding,
        threshold
    )

        # ========================================================
    # FACE MATCH SCORE
    # ========================================================

    distance = float(
        match_result["distance"]
    )

    # Convert the actual face distance into a
    # normalized similarity score.
    face_confidence = max(
        0.0,
        min(
            1.0,
            1.0 - distance
        )
    )

       
    # ========================================================
    # REAL LIVENESS SCORE
    # ========================================================

    liveness_data = live_result["liveness"]

    liveness_confidence = float(
            liveness_data.get(
                "liveness_score",
                0.0
            )
        )

    liveness_confidence = max(
            0.0,
            min(
                1.0,
                liveness_confidence
            )
        )


    # ========================================================
    # REAL LIVENESS SCORE FROM 68-POINT LANDMARKS
    # ========================================================

    liveness_confidence = float(
        liveness_data.get(
            "liveness_score",
            0.0
        )
    )

    liveness_confidence = max(
        0.0,
        min(
            1.0,
            liveness_confidence
        )
    )


    # Liveness must also pass the detector
    liveness_passed = bool(
        liveness_data.get("live", False)
    )


    

    # ========================================================
    # PROCESSING TIME
    # ========================================================

    processing_time_ms = int(
        (time.perf_counter() - start_time) * 1000
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "face_match": bool(
            match_result["verified"]
        ),

        "face_confidence": round(
            face_confidence,
            2
        ),

        "liveness_passed": liveness_passed,

        "liveness_confidence": round(
            liveness_confidence,
            2
        ),

        "spoof_probability": None,

        "processing_time_ms": processing_time_ms
    }
# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("===================================")
    print("       FACE VERIFICATION")
    print("===================================")
    print()

    # --------------------------------------------------------
    # CUSTOMER ID
    # --------------------------------------------------------

    customer_id = input(
        "Enter Customer ID: "
    ).strip()

    if not customer_id:

        print()
        print(
            "❌ Customer ID cannot be empty."
        )

        raise SystemExit

    print()
    print(
        f"Customer selected: {customer_id}"
    )

    # --------------------------------------------------------
    # DEVELOPMENT PATH
    # --------------------------------------------------------

    stored_embedding_path = (
        f"data/embeddings/{customer_id}.npy"
    )

    print()
    print(
        "Loading registered face embedding..."
    )

    print(
        f"Path: {stored_embedding_path}"
    )

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    try:

        stored_embedding = load_embedding(
            stored_embedding_path
        )

    except FileNotFoundError:

        print()
        print(
            "❌ Customer embedding not found."
        )

        print(
            f"Expected:"
        )

        print(
            f"  {stored_embedding_path}"
        )

        raise SystemExit

    except Exception as e:

        print()
        print(
            f"❌ Error loading embedding: {e}"
        )

        raise SystemExit

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if stored_embedding.shape != (128,):

        print()
        print(
            "❌ Invalid embedding."
        )

        print(
            f"Expected: (128,)"
        )

        print(
            f"Received: {stored_embedding.shape}"
        )

        raise SystemExit

    print()
    print(
        f"✅ Customer embedding loaded: "
        f"{stored_embedding.shape}"
    )

    # ========================================================
    # VERIFY
    # ========================================================

    result = verify_customer(
        customer_id=customer_id,
        stored_embedding=stored_embedding,
        threshold=FACE_DISTANCE_THRESHOLD,
        camera_index=CAMERA_INDEX,
        show_window=True
    )
    # ========================================================
    # FINAL JSON RESULT
    # ========================================================

    print(json.dumps(
        result,
        indent=2
    ))