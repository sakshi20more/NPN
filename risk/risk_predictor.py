def calculate_risk(
    face_distance,
    liveness_passed,
    yolo_confidence,
    multiple_faces,
    failed_attempts=0
):
    risk = 0

    # Face matching
    if face_distance > 0.60:
        risk += 40
    elif face_distance > 0.50:
        risk += 20

    # Liveness
    if not liveness_passed:
        risk += 40

    # YOLO detection confidence
    if yolo_confidence < 0.50:
        risk += 10
    elif yolo_confidence < 0.70:
        risk += 5

    # Multiple people
    if multiple_faces:
        risk += 30

    # Failed attempts
    if failed_attempts >= 3:
        risk += 20

    risk = min(risk, 100)

    if risk < 20:
        level = "LOW"
    elif risk < 50:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "risk_score": risk,
        "risk_level": level
    }