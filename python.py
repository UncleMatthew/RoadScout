import cv2

def initialize_camera(camera_index=0, width=320, height=240, fps=15):
    """
    Initializes the webcam with the given parameters.
    
    Parameters:
        camera_index (int): Index of the camera to use.
        width (int): Width of the video capture.
        height (int): Height of the video capture.
        fps (int): Frames per second for the video capture.
        
    Returns:
        cap: The initialized VideoCapture object.
    """
    # Use Video4Linux2 backend by specifying cv2.CAP_V4L2 (for Linux)
    cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
    
    # Set camera resolution and frame rate
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    
    return cap

