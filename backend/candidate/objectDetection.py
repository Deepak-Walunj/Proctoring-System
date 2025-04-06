import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python.vision import ObjectDetector, ObjectDetectorOptions, RunningMode
from mediapipe.tasks.python import BaseOptions
import os
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

# model_path = r"Semester_project/backend/interviewee/efficientdet.tflite"
# model_path = r"C:/Development/Web-Dev/Project-1/Semester_project/backend/interviewee/efficientdet.tflite"
modelpath = os.path.join(os.path.dirname(__file__), "efficientdet.tflite")

class ObjectDetectionModule:
    DEFAULT_MODEL_PATH =modelpath
    # DEFAULT_MODEL_PATH = r"C:\\Users\\Deepak\\OneDrive\\Desktop\\3rd year college Industry project\\Proctoring(Self)\\student_verification\\efficientdet.tflite"
    CHEATING_MATERIALS = ["backpack", "handbag", "laptop", "mouse", "keyboard", "cell phone", "book"]
    def __init__(self, model_path=None, score_threshold=0.3):
        model_path = model_path or self.DEFAULT_MODEL_PATH
        if not os.path.exists(model_path):
            raise ValueError(f"Model file not found at {model_path}. Ensure the path is correct.")
        # print(f"Initializing with model_path: {model_path}")
        self.detector = self._initialize_detector(model_path, score_threshold)
    
    def _initialize_detector(self, model_path, score_threshold):
        # print(f"Model path: {model_path}")
        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            max_results=-1,
            category_allowlist=["backpack", "handbag", "laptop", "mouse", "keyboard", "cell phone", "book"],
            running_mode=RunningMode.IMAGE,  
            score_threshold=score_threshold,
        )
        return ObjectDetector.create_from_options(options)
    
    def detect_cheating(self, frame):
        toast=""
        label = ""
        font_scale = 0.5  
        thickness = 2
        height, width, _ = frame.shape
        top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
        cheatingMaterial_status = False
        cheating_materials = ["backpack", "handbag", "laptop", "mouse", "keyboard", "cell phone", "book"]
        detected_labels = set()
        try:
            frame, detection_result = self.detect_and_draw(frame)
        except Exception as e:
            print(f"[Error in detect_and_draw]: {e}")
            toast="Error in object detection system"
            return frame, cheatingMaterial_status, list(detected_labels)
        if detection_result and detection_result.detections:
            for detection in detection_result.detections:
                label = detection.categories[0].category_name
                if label in cheating_materials:
                    cheatingMaterial_status = True
                    detected_labels.add(label)
                    toast=f"{label} detected!"
            offset = 20 
            for i, label in enumerate(detected_labels):
                y_position = top_left_y + (i + 1) * offset
                cv.putText(frame, f"{label.capitalize()} detected inside the box",
                        (top_left_x, y_position+int(height*0.18)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
        return frame, cheatingMaterial_status, detected_labels, toast
    
    def detect_and_draw(self, frame):
        if not self.detector:
            try:
                self._initialize_detector()
            except Exception as e:
                print(f"[Error] during detector initialization: {e}")
                return frame, None 
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result=None
        try:
            detection_result = self.detector.detect(mp_image) 
        except Exception as e:
            print(f"[Error] in detecting cheating: {e}")
        if detection_result is not None:
            frame = self._draw_detections(frame, detection_result)
        else:
            print("[Warning] No detections were made.")
        return frame, detection_result

    def _draw_detections(self, frame, detection_result):
        if not (detection_result and detection_result.detections):
            # print("[Info] No detections to draw.")
            return frame
        font_scale=0.5
        thickness=2
        if detection_result and detection_result.detections:
            for detection in detection_result.detections:
                bounding_box = getattr(detection, "bounding_box", None)
                if not bounding_box:
                    print("[Warning] Detection missing bounding box, skipping.")
                    continue
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
                    cv.putText(frame, label, (x_min, y_min - 10), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
        return frame

def initialize_camera(width=640, height=480, fps=1):
    camStart_status=False
    try:
        cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv.CAP_PROP_FPS, fps)
        if not cap.isOpened():
            print("Error: Camera could not be accessed.")
            return camStart_status, None
        camStart_status=True
        return camStart_status, cap
    except Exception as e:
        print(f"[Error] while initialising the camera :{e}")
        return camStart_status, None

if __name__ == "__main__":
    cond, cap = initialize_camera()
    if cond:
        obj = ObjectDetectionModule()
        while True:
            ret, frame = cap.read()
            frame = cv.flip(frame, 1)
            if not ret:
                print("Failed to capture frame. Exiting...")
                break
            frame, cheatingMaterial_status, label, toast=obj.detect_cheating(frame)
            cv.imshow("Camera", frame)
            key = cv.waitKey(1)
            if key == 27: 
                print("Exiting...")
                break
            elif key == 13: 
                cv.imwrite("resultImages/object_detected.jpg", frame)
                print("Image saved successfully.")
                break
        cap.release()
        cv.destroyAllWindows()
    else:
        print("Exiting")
