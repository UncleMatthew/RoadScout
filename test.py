from ultralytics import YOLO

def setup_model():
    model = YOLO("yolov5nu.pt")
    return model

if __name__ == "__main__":
    print("Loading YOLO model...")
    model = setup_model()
    print("YOLO model loaded successfully.")

