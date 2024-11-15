import cv2

def test_camera(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Cannot open camera at index {index}")
    else:
        print(f"Camera at index {index} opened successfully")
    cap.release()

# Test camera indices
test_camera(0)
test_camera(1)
test_camera(2)

