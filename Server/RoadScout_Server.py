import cv2
import socket
import time
from threading import Thread
from ultralytics import YOLO
from rich.console import Console
from rich.table import Table
import numpy as np  # Ensure numpy is imported

# Constants
VIDEO_PORT = 5000

# Stats Tracker
stats = {
    "Connection Status": "Disconnected",
    "Last Processed Frame": "N/A",
    "Inference Time (ms)": "N/A",
}

# Rich Console for Terminal UI
console = Console()


def display_terminal_ui():
    """Continuously update and display the terminal UI with stats."""
    while True:
        console.clear()
        console.rule("[bold blue]RoadScout Server[/bold blue]")
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Metric", justify="left")
        table.add_column("Value", justify="left")

        for key, value in stats.items():
            table.add_row(key, str(value))

        console.print(table)
        time.sleep(1)  # Refresh every second


def update_stat(key, value):
    """Update stats dynamically in the terminal UI."""
    stats[key] = value


def initialize_model():
    """Initialize YOLOv8 model."""
    model = YOLO("yolov8n.pt")  # Use other weights for better accuracy (e.g., yolov8m.pt)
    model.conf = 0.5
    return model


def process_video():
    """Process incoming video from the client."""
    model = initialize_model()
    update_stat("Connection Status", "Waiting for Connection")

    # Start server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", VIDEO_PORT))
    sock.listen(5)

    while True:
        try:
            conn, addr = sock.accept()
            update_stat("Connection Status", f"Connected to {addr[0]}")

            data = b""
            while True:
                packet = conn.recv(4096)
                if not packet:
                    update_stat("Connection Status", "Disconnected")
                    break

                data += packet
                a = data.find(b'\xff\xd8')
                b = data.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = data[a:b+2]
                    data = data[b+2:]
                    frame = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)

                    # Inference
                    start_time = time.time()
                    results = model.predict(frame, stream=False)
                    inference_time = (time.time() - start_time) * 1000

                    # Draw bounding boxes
                    for result in results:
                        for box in result.boxes:
                            x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
                            cls = int(box.cls[0])
                            conf = box.conf[0]
                            if cls == 2:  # Class 2 corresponds to 'Car'
                                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                                cv2.putText(
                                    frame,
                                    f"Car: {conf:.2f}",
                                    (x_min, y_min - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5,
                                    (0, 255, 0),
                                    2,
                                )

                    # Display the camera feed
                    cv2.imshow("RoadScout - Camera View", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    # Update stats
                    update_stat("Last Processed Frame", time.strftime("%H:%M:%S"))
                    update_stat("Inference Time (ms)", f"{inference_time:.2f}")

            conn.close()
        except Exception as e:
            update_stat("Connection Status", f"Error: {e}")


if __name__ == "__main__":
    # Start the terminal UI in a separate thread
    Thread(target=display_terminal_ui, daemon=True).start()

    # Start processing video
    process_video()
