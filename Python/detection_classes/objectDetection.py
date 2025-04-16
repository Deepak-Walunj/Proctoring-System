import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python.vision import ObjectDetector, ObjectDetectorOptions, RunningMode
from mediapipe.tasks.python import BaseOptions
import os
import time
from pathlib import Path

class ObjectDetectionModule:
    
    def __init__(self, model_path=None, score_threshold=0.3):
        if model_path is None:
            model_path = "efficientdet.tflite"
        print(f"[DEBUG] Received model_path: {model_path}")
        if not os.path.isabs(model_path):
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_path)
        print(f"[DEBUG] Absolute model_path before existence check: {model_path}")
        if not os.path.exists(model_path):
            raise ValueError(f"Model file not found at {model_path}")
            
        self.model_path = model_path
        print(f"[DEBUG] Final model path: {self.model_path}")
        self.CHEATING_MATERIALS = ["backpack", "handbag", "laptop", "mouse", "keyboard", "cell phone", "book"]
        self.detector = self._initialize_detector(self.model_path, score_threshold)
        self.previous_objects = dict()  # Store objects from the previous frame
        self.object_count = {item: 0 for item in self.CHEATING_MATERIALS}
        
    def _initialize_detector(self, model_path, score_threshold):
        model_path = os.path.relpath(model_path, os.getcwd())
        model_path = model_path.replace("\\", "/")
        model_path = Path(model_path).resolve(strict=True)  
        print(f"Model path: {model_path}")
        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            max_results=-1,
            category_allowlist=self.CHEATING_MATERIALS,
            running_mode=RunningMode.IMAGE,  
            score_threshold=score_threshold,
        )
        return ObjectDetector.create_from_options(options)
    
    def detect_cheating(self, frame):
        font_scale = 0.5  
        thickness = 2
        height, width, _ = frame.shape
        top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
        cheating_material_status = False
        detected_labels = set()
        toast = ""
        
        try:
            frame, detection_result = self.detect_and_draw(frame)
        except Exception as e:
            print(f"[Error in detect_and_draw]: {e}")
            toast = "Error in object detection system"
            return frame, cheating_material_status, self.object_count, toast 
        
        if detection_result and detection_result.detections:
            for detection in detection_result.detections:
                if detection.categories and detection.categories[0].score >= 0.35:
                    label = detection.categories[0].category_name
                    if label in self.CHEATING_MATERIALS:
                        cheating_material_status = True
                        detected_labels.add(label)
                        toast=f"{label} detected!"
        
        for obj in detected_labels:
            if obj in self.previous_objects:
                self.previous_objects[obj] = (self.previous_objects[obj][0] + 1, 0)  # Increment detection count, reset missing count
            else:
                self.previous_objects[obj] = (1, 0)  # New object detected
        
        objects_to_remove = []
        for obj in list(self.previous_objects.keys()):
            if obj not in detected_labels:
                self.previous_objects[obj] = (self.previous_objects[obj][0], self.previous_objects[obj][1] + 1)  # Increment missing count
                if self.previous_objects[obj][1] > 20:  # If object disappears for more than 20 frames
                    objects_to_remove.append(obj)
        
        # Remove objects that disappeared too long
        for obj in objects_to_remove:
            del self.previous_objects[obj]
        
        #confirmation code
        # Update object count only when the object appears for 1 sec
        for obj in detected_labels:
            if self.previous_objects[obj][0] == 10:  # First appearance in this session
                self.object_count[obj] += 1
        offset = 20
        for i, label in enumerate(detected_labels):
            y_position = top_left_y + (i + 1) * offset
            cv.putText(frame, f"{label.capitalize()} detected inside the box",
                    (top_left_x, y_position + int(height * 0.18)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
        return frame, cheating_material_status, self.object_count, toast

    def detect_and_draw(self, frame):
        if not self.detector:
            raise RuntimeError("Object detector is not initialized.")
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = self.detector.detect(mp_image)
        if detection_result:
            frame = self._draw_detections(frame, detection_result)
        return frame, detection_result

    def _draw_detections(self, frame, detection_result):
        font_scale = 0.5
        thickness = 2
        if detection_result and detection_result.detections:
            for detection in detection_result.detections:
                bounding_box = detection.bounding_box
                if not bounding_box:
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
    try:
        cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv.CAP_PROP_FPS, fps)
        if not cap.isOpened():
            print("Error: Camera could not be accessed.")
            return False, None
        return True, cap
    except Exception as e:
        print(f"[Error initializing camera]: {e}")
        return False, None

if __name__ == "__main__":
    cond, cap = initialize_camera()
    if cond:
        obj = ObjectDetectionModule()
        while True:
            start_time1=time.time()
            start_time = time.time()
            ret, frame = cap.read()
            frame = cv.flip(frame, 1)
            if not ret:
                print("Failed to capture frame. Exiting...")
                break
            frame, cheatingMaterial_status, object_count, toast = obj.detect_cheating(frame)
            # print("Appearance Counts:", object_count)
            print(toast)
            cv.imshow("Camera", frame)
            key = cv.waitKey(1)
            elapsed_time = time.time() - start_time1
            sleep_time = max(0, 0.1 - elapsed_time)
            time.sleep(sleep_time)
            if key == 27 or key==13:
                print("Exiting...")
                print("Appearance Counts:", object_count)
                break
            elapsed_time = time.time() - start_time
            sleep_time = max(0, 0.1 - elapsed_time)
            time.sleep(sleep_time)
        cap.release()
        cv.destroyAllWindows()
    else:
        print("Exiting")
