import cv2
import socket
import time
import os
import json
from threading import Thread
from rich.console import Console
from rich.table import Table

# Constants
VIDEO_PORT = 5000
CONFIG_FILE = "client_config.json"  # File to store the saved settings

# Stats Tracker
stats = {
    "Server IP": "Not connected",
    "Camera ID": "N/A",
    "Connection Status": "Disconnected",
    "Last Frame Sent": "N/A",
}

# Rich Console for Terminal UI
console = Console()


def display_terminal_ui():
    """Continuously update and display the terminal UI with stats."""
    while True:
        console.clear()
        console.rule("[bold blue]RoadScout Client[/bold blue]")
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


def load_saved_settings():
    """Load the saved settings (IP address and camera ID) from the configuration file, if it exists."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}


def save_settings(settings):
    """Save the settings (IP address and camera ID) to the configuration file."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(settings, file)


def prompt_for_settings():
    """Prompt the user for the server IP address and camera ID."""
    settings = load_saved_settings()

    # Prompt for server IP
    server_ip = settings.get("server_ip")
    if server_ip:
        console.print(f"[cyan]Previously saved server IP: {server_ip}[/cyan]")
        use_saved_ip = input("Do you want to use the saved IP? (y/n): ").strip().lower()
        if use_saved_ip != "y":
            server_ip = input("Enter the server IP address: ").strip()
    else:
        server_ip = input("Enter the server IP address: ").strip()
    update_stat("Server IP", server_ip)

    # Prompt for camera ID
    camera_id = settings.get("camera_id")
    if camera_id is not None:
        console.print(f"[cyan]Previously saved camera ID: {camera_id}[/cyan]")
        use_saved_camera = input("Do you want to use the saved camera ID? (y/n): ").strip().lower()
        if use_saved_camera != "y":
            camera_id = int(input("Enter the camera ID: ").strip())
    else:
        camera_id = int(input("Enter the camera ID: ").strip())
    update_stat("Camera ID", camera_id)

    # Ask if settings should be saved
    save_option = input("Do you want to save these settings for future sessions? (y/n): ").strip().lower()
    if save_option == "y":
        save_settings({"server_ip": server_ip, "camera_id": camera_id})

    return server_ip, camera_id


def stream_video(server_ip, camera_id):
    """Stream video to the server."""
    while True:
        try:
            # Attempt to connect to the server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server_ip, VIDEO_PORT))
            update_stat("Connection Status", "Connected")

            # Capture video
            cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)  # Use V4L2 backend
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)

            if not cap.isOpened():
                update_stat("Connection Status", "Camera Access Error")
                console.print(f"[red]Unable to access camera with ID {camera_id}[/red]")
                return

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                _, buffer = cv2.imencode('.jpg', frame)
                sock.sendall(buffer.tobytes())
                update_stat("Last Frame Sent", time.strftime("%H:%M:%S"))

            cap.release()
            sock.close()
            break  # Exit if streaming completes successfully
        except socket.error as e:
            update_stat("Connection Status", "Disconnected")
            console.print(f"[red]Connection failed to {server_ip}: {e}[/red]")
            time.sleep(5)


if __name__ == "__main__":
    # Prompt for server IP and camera ID before starting the UI
    server_ip, camera_id = prompt_for_settings()

    # Start the terminal UI in a separate thread
    Thread(target=display_terminal_ui, daemon=True).start()

    # Start video streaming
    stream_video(server_ip, camera_id)
