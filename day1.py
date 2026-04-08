from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

results = model("traffic.jpg")

# Get annotated image
annotated = results[0].plot()

# Show using OpenCV
cv2.imshow("Detection", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()

print("Detection complete!")