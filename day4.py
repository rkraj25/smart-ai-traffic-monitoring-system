from ultralytics import YOLO
import cv2
import time

# Load model
model = YOLO("yolov8n.pt")

# Load video
cap = cv2.VideoCapture("traffic.mp4")

vehicle_classes = [2, 3, 5, 7]

if not cap.isOpened():
    print("Error: Cannot open video")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    start = time.time()

    results = model(frame)
    result = results[0]

    count = 0

    # Count vehicles
    if result.boxes is not None:
        for box in result.boxes:
            cls = int(box.cls[0])
            if cls in vehicle_classes:
                count += 1

    # 🚦 Density logic
    if count < 8:
        density = "Low"
        color = (0, 255, 0)     # Green
    elif count < 20:
        density = "Medium"
        color = (0, 255, 255)   # Yellow
    else:
        density = "High"
        color = (0, 0, 255)     # Red

    # Draw boxes
    annotated = result.plot()

    # Show count
    cv2.putText(annotated, f"Vehicles: {count}", (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show density
    cv2.putText(annotated, f"Traffic: {density}", (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    # FPS
    end = time.time()
    fps = 1 / (end - start)

    cv2.putText(annotated, f"FPS: {int(fps)}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Traffic Monitoring System", annotated)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()