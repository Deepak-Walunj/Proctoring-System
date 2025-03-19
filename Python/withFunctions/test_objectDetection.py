import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python.vision import ObjectDetector, ObjectDetectorOptions, RunningMode
from mediapipe.tasks.python import BaseOptions

def init_camera():
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)  # Use 0 for the default camera
    if not cap.isOpened():
        print("Error: Could not open the camera.")
        False, None
    else:
        print("Camera initialized successfully.")
    return True, cap

def create_options(print_result_callback):
    """Initialize the object detector with the specified model."""
    try:
        model_path = "efficientdet.tflite"
        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            max_results=-1,
            category_allowlist=["person","backpack", "handbag", "laptop", "mouse", "keyboard", "cell phone", "book"],
            running_mode=RunningMode.LIVE_STREAM,
            result_callback=print_result_callback,
            score_threshold=0.35
        )
        # print(f"options: {options}")
        return True, options
        
    except Exception as e:
        print(f"An error occured {e}")
        return False, None

def draw_detections(frame, result_container):
    detection_result = result_container.get("detection_result")
    if detection_result and detection_result.detections:
        for detection in detection_result.detections:
            bounding_box = detection.bounding_box
            x_min = int(bounding_box.origin_x)
            y_min = int(bounding_box.origin_y)
            width = int(bounding_box.width)
            height = int(bounding_box.height)
            # Draw bounding boxes
            cv.rectangle(frame, (x_min, y_min), (x_min + width, y_min + height), (0, 255, 0), 2)
            # Draw labels
            if detection.categories:
                category = detection.categories[0]
                label = f"{category.category_name} ({category.score:.2f})"
                cv.putText(frame, label, (x_min, y_min - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    else:
        print("No detections available for the current frame.")
    return frame

def detectObjects(frame, detector, result_container):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        frame_timestamp_ms = int(cv.getTickCount() / cv.getTickFrequency() * 1000)
        detector.detect_async(mp_image, frame_timestamp_ms)
        frame= draw_detections(frame, result_container)
        key=cv.waitKey(1)
        if key == 27:  # Esc key
            return "exit", frame
        elif key == 13:  # Enter key
            return "capture", frame
        return None, frame  # No special action

if __name__ == "__main__":
    cond, cap = init_camera()
    if cond==True:
        result_container = {"detection_result": None}
        def print_result(result, output_image, timestamp_ms):
            result_container["detection_result"] = result
        _, options = create_options(print_result)  # Dummy callback
        detector = ObjectDetector.create_from_options(options)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame. Exiting...")
                exit()
            action, frame1=detectObjects(frame, detector, result_container)
            cv.imshow("Camera", frame1)

            if action=="exit":  # Esc key to exit
                print("Exiting...")
                break
            elif action == "capture":  # Enter key to save the current frame
                cv.imwrite("resultImages/object_detected.jpg", frame1)
                print("Image saved successfully.")
                break
        cap.release()
        cv.destroyAllWindows()
        exit()
    elif cond==False:
        print("Exiting")
        exit()