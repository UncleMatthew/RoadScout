RoadScout V0.01

RoadScout is a vehicle tracking and analytics system designed to process live camera feeds to detect and count vehicles in real time. It utilizes cutting-edge machine learning and computer vision technologies to provide insights into road utilization, parking lot usage, and vehicle activity trends.
Features

    Real-Time Vehicle Detection:
        Processes video streams to detect vehicles using YOLOv8, a state-of-the-art object detection model.
    Analytics:
        Tracks total vehicle counts and unique vehicles based on their appearances.
        Records timestamped data for detailed analysis.
    Client-Server Architecture:
        Client: Captures video using a USB camera connected to a Raspberry Pi and streams it to the server.
        Server: Processes the stream using YOLOv8, tracks analytics, and displays both live statistics and bounding-boxed visuals.
    Terminal-Based UI:
        Displays dynamic stats in a clean and interactive terminal interface using rich.
    Pop-Out Camera View:
        Displays bounding boxes on detected vehicles in a separate window.

Intended Use Cases

    Tracking Parking Lot Analytics:
        Analyze parking lot usage by monitoring the number of cars entering and leaving.
        Understand peak usage times and average duration of stay.

    Tracking Road Utilization:
        Monitor vehicle flow on roads to identify bottlenecks or underutilized areas.
        Use data to inform urban planning or road network improvements.

    Other Use Cases:
        Event Planning and Logistics:
            Measure traffic near event venues to optimize parking and road access.
        Retail and Commercial Analytics:
            Monitor traffic near retail outlets to assess potential customer reach.
        Environmental Impact Studies:
            Use vehicle count data to estimate traffic-related emissions.
        Accident Prevention and Safety Improvements:
            Identify high-traffic zones and implement measures to reduce congestion-related risks.

Technologies Used

    Object Detection:
        YOLOv8: (You Only Look Once, Version 8) A neural network model optimized for real-time object detection, providing high accuracy and speed.

    Client-Server Communication:
        Socket Programming: Establishes a TCP connection between the client (Raspberry Pi) and the server for real-time video transmission.

    Real-Time Analytics:
        OpenCV: Processes video streams and draws bounding boxes on detected vehicles.
        Rich Library: Provides an intuitive and dynamic terminal interface for displaying live stats.

    Raspberry Pi Integration:
        Configured as a lightweight, portable client for capturing and streaming video.

    Python:
        The entire application is built using Python for its robust libraries and ease of deployment.

How It Works

    Client:
        Captures video using a USB camera.
        Streams the video to the server via a TCP connection.

    Server:
        Processes incoming video streams using YOLOv8 for vehicle detection.
        Tracks the number of cars and unique vehicles over time.
        Updates a terminal-based UI with real-time stats and shows a pop-out window with the live video feed and bounding boxes.

    Output:
        Provides analytics on the number of vehicles detected and unique vehicles identified.
        Enables live visualization of camera data.

Setup Instructions
Requirements

    Client:
        Raspberry Pi with Python 3 installed.
        USB camera.
        WiFi connection.
    Server:
        A machine with Python 3 and an NVIDIA GPU (for accelerated inference).
        Libraries: ultralytics, rich, opencv-python, numpy.

Installation

    Clone the repository:

git clone https://github.com/your-username/RoadScout.git
cd RoadScout

Install dependencies:

pip install -r requirements.txt

Start the client:

python roadscout_client.py

Start the server:

    python roadscout_server_terminal.py

Future Improvements

    Multi-Camera Support:
        Handle multiple camera streams for larger-scale monitoring.
    Expanded Analytics:
        Provide detailed breakdowns of vehicle counts by time intervals or zones.
    Dashboard Integration:
        Develop a web-based dashboard for remote monitoring and reporting.
    Vehicle Type Classification:
        Extend detection to classify vehicle types (e.g., cars, trucks, buses).
