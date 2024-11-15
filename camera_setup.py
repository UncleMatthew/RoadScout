import cv2

def initialize_camera():
    cap = cv2.VideoCapture(0)  # Use appropriate camera index
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    return cap

