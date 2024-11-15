# camera_setup.py
import cv2

def initialize_cameras(max_cameras=10):
    caps = []
    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap is not None and cap.isOpened():
            print(f"Camera at index {index} opened successfully.")
            caps.append((index, cap))
        else:
            cap.release()
    if not caps:
        print("No cameras could be opened.")
        exit()
    return caps

