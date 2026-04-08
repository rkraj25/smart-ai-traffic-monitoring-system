from ultralytics import YOLO
import cv2
import time

# Load YOLO model
model = YOLO("yolov8n.pt")

# Load video
cap = cv2.VideoCapture("traffic.mp4")

# Check if video opened
if not cap.isOpened():
    print("Error: Cannot open video")
    exit()

while True:
    ret, frame = cap.read()

    # Stop when video ends
    if not ret:
        break

    # Resize frame for better performance
    frame = cv2.resize(frame, (640, 480))

    # Start time (for FPS)
    start = time.time()

    # Run detection (NO stream=True → easier)
    results = model(frame)

    # Get annotated frame
    annotated = results[0].plot()

    # Calculate FPS
    end = time.time()
    fps = 1 / (end - start)

    # Show FPS
    cv2.putText(annotated, f"FPS: {int(fps)}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display video
    cv2.imshow("Traffic Detection", annotated)

    # Press ESC to exit
    if cv2.waitKey(1) == 27:
        break

# Release everything
cap.release()
cv2.destroyAllWindows()