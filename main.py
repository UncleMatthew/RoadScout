import cv2
import time
import configparser
from ultralytics import YOLO
from camera_setup import initialize_camera
from sort import Sort
import threading
import openpyxl
from openpyxl import Workbook
import os
import numpy as np
import zipfile  # For exception handling in save_to_excel

# Import the vehicle_id_manager module
import vehicle_id_manager

def setup_model():
    model = YOLO("yolov5nu.pt")
    return model

def detect_objects(model, frame, conf_threshold):
    results = model(frame)
    detections = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            confidence = box.conf.item()
            if confidence < conf_threshold:
                continue  # Skip detections with low confidence

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            class_id = int(box.cls.item())
            detections.append([x1, y1, x2, y2, confidence, class_id])

    return detections

def save_to_excel(data, excel_file):
    try:
        if os.path.exists(excel_file):
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
        else:
            # Create a new workbook and add header
            wb = Workbook()
            ws = wb.active
            ws.append(['Timestamp', 'Vehicle Count', '', '', 'Total Vehicles per Hour', 'Unique Vehicles per Hour'])
    except (FileNotFoundError, zipfile.BadZipFile, openpyxl.utils.exceptions.InvalidFileException):
        print(f"Excel file not found or invalid. Creating a new file: {excel_file}")
        wb = Workbook()
        ws = wb.active
        ws.append(['Timestamp', 'Vehicle Count', '', '', 'Total Vehicles per Hour', 'Unique Vehicles per Hour'])
    except Exception as e:
        print(f"Error loading workbook: {e}")
        return  # Optionally handle other exceptions or re-raise

    ws.append(data)
    wb.save(excel_file)

def process_webcam():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    conf_threshold = float(config['Detection']['conf_threshold'])
    excel_file = config['Export']['excel_file']

    # SORT tracker parameters
    max_age = int(config['Tracking']['max_age'])
    min_hits = int(config['Tracking']['min_hits'])
    iou_threshold = float(config['Tracking']['iou_threshold'])

    # Read update interval from settings or default to 10 seconds
    update_interval = int(config.get('Update', 'update_interval', fallback=10))

    cap = initialize_camera()
    model = setup_model()
    tracker = Sort(max_age=max_age, min_hits=min_hits, iou_threshold=iou_threshold)

    # Load existing vehicle IDs
    tracked_vehicle_ids, vehicle_id_timestamps = vehicle_id_manager.load_vehicle_ids('vehicle_ids.json')

    print(f"Starting with {len(tracked_vehicle_ids)} tracked vehicle IDs.")

    DESIRED_FPS = int(config['Camera']['fps'])
    frame_interval = 1 / DESIRED_FPS
    last_frame_time = 0
    frame_skip_interval = 1  # Process every frame
    frame_counter = 0

    # Load class names for the COCO dataset
    class_names = model.names

    # For counts over the past hour
    interval_counts = []  # List of (timestamp, set of vehicle IDs counted)

    # Timer for updating every update_interval seconds
    last_update_time = time.time()

    try:
        while cap.isOpened():
            current_time = time.time()
            if current_time - last_frame_time < frame_interval:
                time.sleep(0.01)
                continue

            last_frame_time = current_time
            ret, frame = cap.read()
            if not ret:
                break

            frame_counter += 1
            if frame_counter % frame_skip_interval != 0:
                continue  # Skip frames to reduce processing load if necessary

            frame_resized = cv2.resize(frame, (640, 480))

            # Detect objects
            detections = detect_objects(model, frame_resized, conf_threshold)

            # Prepare detections for SORT
            sort_detections = []
            for det in detections:
                x1, y1, x2, y2, confidence, class_id = det
                class_name = class_names[class_id]
                if class_name in ['car', 'truck']:
                    sort_detections.append([x1, y1, x2, y2, confidence])

            if len(sort_detections) > 0:
                sort_detections = np.array(sort_detections)
            else:
                sort_detections = np.empty((0, 5))

            # Update tracker
            tracks = tracker.update(sort_detections)

            # Set to keep track of vehicle IDs in the current frame
            current_vehicle_ids = set()

            # Update vehicle IDs and timestamps
            for track in tracks:
                x1, y1, x2, y2, track_id = track
                track_id = int(track_id)
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                label = f"vehicle ID {track_id}"
                color = (0, 255, 0)  # Green color for vehicles

                cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame_resized, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # Update tracked IDs and timestamps
                if track_id not in tracked_vehicle_ids:
                    tracked_vehicle_ids.add(track_id)
                    print(f"New vehicle detected: ID {track_id}")
                vehicle_id_timestamps[track_id] = current_time

                current_vehicle_ids.add(track_id)

            # Remove old vehicle IDs from vehicle_id_timestamps
            vehicle_id_timestamps = {id: t for id, t in vehicle_id_timestamps.items() if current_time - t <= 3600}

            # Update interval_counts
            interval_counts.append((current_time, current_vehicle_ids.copy()))

            # Remove old entries beyond one hour
            interval_counts = [(t, ids) for t, ids in interval_counts if current_time - t <= 3600]

            # Update and save to Excel every update_interval seconds
            if current_time - last_update_time >= update_interval:
                # Compute total vehicles per hour (unique vehicle IDs seen in the past hour)
                total_vehicle_ids = set()
                for _, ids in interval_counts:
                    total_vehicle_ids.update(ids)
                total_vehicles_per_hour = len(total_vehicle_ids)

                # Compute unique vehicles per hour (vehicle IDs currently being tracked)
                unique_vehicles_per_hour = len(vehicle_id_timestamps)

                # For current frame vehicle count, use the number of vehicles currently being tracked
                interval_vehicle_count = len(current_vehicle_ids)

                timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
                data = [timestamp_str, interval_vehicle_count, '', '', total_vehicles_per_hour, unique_vehicles_per_hour]
                save_to_excel(data, excel_file)
                print(f"Data saved to {excel_file} at {timestamp_str}")
                last_update_time = current_time  # Reset last update time

            cv2.imshow("Vehicle Detection and Tracking", frame_resized)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Save vehicle IDs when the program is closed
        vehicle_id_manager.save_vehicle_ids(tracked_vehicle_ids, vehicle_id_timestamps, 'vehicle_ids.json')
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    process_webcam()

