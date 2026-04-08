import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from collections import deque
from datetime import datetime
import time

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(layout="wide")

# -------------------------------
# DB SETUP
# -------------------------------
conn = sqlite3.connect("traffic.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS traffic")

cursor.execute("""
CREATE TABLE traffic (
    time TEXT,
    count INTEGER,
    density TEXT,
    accuracy REAL
)
""")
conn.commit()

# -------------------------------
# TITLE
# -------------------------------
st.title("🚦 Smart AI Traffic Monitoring System")
st.markdown("YOLOv8m + Tracking + Prediction + Analytics Dashboard")

# -------------------------------
# LOAD MODEL
# -------------------------------
model = YOLO("yolov8m.pt")

CAR = 2
BIKE = 3
BUS = 5
TRUCK = 7

vehicle_classes = [CAR, BIKE, BUS, TRUCK]

video_file = st.file_uploader(
    "Upload Traffic Video",
    type=["mp4", "avi", "mov"]
)

if video_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())

    cap = cv2.VideoCapture(tfile.name)

    stframe = st.empty()

    history = deque(maxlen=20)
    unique_ids = set()

    data = []

    final_accuracy = 0
    density = "Low"

    car_count = 0
    bike_count = 0
    bus_count = 0
    truck_count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # -------------------------------
        # BETTER FRAME SIZE
        # -------------------------------
        frame = cv2.resize(frame, (960, 540))

        # -------------------------------
        # YOLO TRACKING
        # -------------------------------
        results = model.track(
            frame,
            persist=True,
            conf=0.5
        )

        result = results[0]

        total_count = 0
        conf_scores = []

        car_count = 0
        bike_count = 0
        bus_count = 0
        truck_count = 0

        if result.boxes is not None:
            for box in result.boxes:

                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls in vehicle_classes:
                    total_count += 1
                    conf_scores.append(conf)

                if cls == CAR:
                    car_count += 1
                elif cls == BIKE:
                    bike_count += 1
                elif cls == BUS:
                    bus_count += 1
                elif cls == TRUCK:
                    truck_count += 1

                if box.id is not None:
                    unique_ids.add(int(box.id[0]))

        # -------------------------------
        # ACCURACY
        # -------------------------------
        if conf_scores:
            accuracy = round(
                (sum(conf_scores) / len(conf_scores)) * 100,
                2
            )
        else:
            accuracy = 0

        final_accuracy = accuracy

        # -------------------------------
        # DENSITY
        # -------------------------------
        if total_count < 8:
            density = "Low"
        elif total_count < 20:
            density = "Medium"
        else:
            density = "High"

        # -------------------------------
        # PREDICTION
        # -------------------------------
        history.append(total_count)
        predicted = int(np.mean(history))

        # -------------------------------
        # SAVE DB
        # -------------------------------
        now = datetime.now().strftime("%H:%M:%S")

        cursor.execute(
            "INSERT INTO traffic VALUES (?, ?, ?, ?)",
            (now, total_count, density, accuracy)
        )
        conn.commit()

        # -------------------------------
        # STORE DATA
        # -------------------------------
        data.append({
            "Time": now,
            "Count": total_count,
            "Predicted": predicted,
            "Accuracy": accuracy,
            "Cars": car_count,
            "Bikes": bike_count,
            "Bus": bus_count,
            "Truck": truck_count,
            "Density": density
        })

        # -------------------------------
        # DRAW VIDEO
        # -------------------------------
        annotated = result.plot()

        cv2.putText(
            annotated,
            f"Total: {total_count}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated,
            f"Predicted: {predicted}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated,
            f"Accuracy: {accuracy}%",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated,
            f"Cars:{car_count} Bikes:{bike_count}",
            (20, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            annotated,
            f"Bus:{bus_count} Truck:{truck_count}",
            (20, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        stframe.image(
            annotated,
            channels="BGR",
            use_container_width=True
        )

        time.sleep(0.03)

    cap.release()

    # -------------------------------
    # DASHBOARD
    # -------------------------------
    df = pd.DataFrame(data)

    st.success("✅ Analysis Completed Successfully")

    st.markdown("---")
    st.header("📊 Traffic Analytics Dashboard")

    # -------------------------------
    # GRAPH
    # -------------------------------
    st.subheader("📈 Traffic Trend")

    fig = px.line(
        df,
        x="Time",
        y=["Count", "Predicted"],
        title="Traffic Flow Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # METRICS
    # -------------------------------
    st.subheader("📌 Key Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🚘 Unique Vehicles", len(unique_ids))

    with col2:
        st.metric("🎯 Accuracy", f"{final_accuracy}%")

    with col3:
        st.metric("🚦 Density", density)

    # -------------------------------
    # VEHICLE DISTRIBUTION
    # -------------------------------
    st.subheader("🚗 Vehicle Class Distribution")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Cars", car_count)

    with c2:
        st.metric("Bikes", bike_count)

    with c3:
        st.metric("Bus", bus_count)

    with c4:
        st.metric("Truck", truck_count)

    # -------------------------------
    # TABLE
    # -------------------------------
    st.subheader("📋 Traffic Data Table")
    st.dataframe(df, use_container_width=True)