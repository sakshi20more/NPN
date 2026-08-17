import cv2
from ultralytics import YOLO

# Load face detection model
model = YOLO("models/yolov9t-face-lindevs.pt")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera")
    exit()

print("YOLO face detection started")
print("Press Q to quit")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not read camera frame")
        break

    # Run YOLO
    results = model(frame, conf=0.5, verbose=False)

    # Draw detections
    for result in results:

        for box in result.boxes:

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            confidence = float(box.conf[0])

            # Draw face rectangle
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Display confidence
            cv2.putText(
                frame,
                f"Face: {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            print(
                f"Face detected | Confidence: {confidence:.2f}"
            )

    cv2.imshow(
        "YOLO Face Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()