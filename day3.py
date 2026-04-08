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

    # Get results
    result = results[0]

    count = 0

    # Loop through detected objects
    for box in result.boxes:
        cls = int(box.cls[0])

        if cls in vehicle_classes:
            count += 1

    # Draw detection boxes
    annotated = result.plot()

    # Show vehicle count
    cv2.putText(annotated, f"Vehicles: {count}", (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # FPS calculation
    end = time.time()
    fps = 1 / (end - start)

    cv2.putText(annotated, f"FPS: {int(fps)}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Traffic Detection", annotated)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()