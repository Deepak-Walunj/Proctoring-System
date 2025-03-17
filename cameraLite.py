# import cv2 as cv

def draw_dynamic_box(frame, box_coords, text_top, height, font_scale=0.5, thickness=2):
    """Draws a dynamic box and instructions on the frame."""
    top_x=text_top[0]
    top_y=text_top[1]
    box_x, box_y, box_w, box_h = box_coords
    cv.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 0, 255), 2)
    cv.putText(frame, "Press 'ENTER' to capture photo when your face is inside the box",
            (top_x,top_y), cv.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    cv.putText(frame, "Press 'ESC' to quit",
            (top_x,top_y+ int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

def CameraLite(frame, face_detection, object_detector):
    import cv2 as cv
    # model_path = r"C:\\Users\\Deepak\\OneDrive\\Desktop\\3rd year college Industry project\\Proctoring(Self)\\student_verification\\efficientdet.tflite"
    # object_detector = ObjectDetectionModule(model_path=model_path)
    # face_preprocessor = FacePreprocessing()
    try:
        # with face_preprocessor.mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection:
        height, width, _ = frame.shape
        font_scale = 0.5  
        thickness = 2
        box_coords = (int(width * 0.3), int(height * 0.2), int(width * 0.4), int(height * 0.6))
        top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
        # bottom_right_x, bottom_right_y = int(width * 0.0), int(height * 0.9)
        draw_dynamic_box(frame, box_coords, (top_left_x, top_left_y), height, font_scale, thickness)
        cheating_material_inside_the_box=False
        cheating_materials = ["backpack", "handbag", "laptop", "mouse", "keyboard", "cell phone", "book"]
        label=None
        single_face_inside_the_box = False
        box_faces = 0
        non_box_faces = 0
        try:
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = face_detection.process(rgb_frame)
        except Exception as e:
            print(f"[Error] Face detection failed: {e}")
            results = None
        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                x, y, w, h = (int(bboxC.xmin * width), int(bboxC.ymin * height),
                            int(bboxC.width * width), int(bboxC.height * height))
                # Check if the face is inside the box
                if (box_coords[0] < x < box_coords[0] + box_coords[2] and
                        box_coords[1] < y < box_coords[1] + box_coords[3] and
                        box_coords[0] < x + w < box_coords[0] + box_coords[2] and
                        box_coords[1] < y + h < box_coords[1] + box_coords[3]):
                    box_faces += 1
                else:
                    non_box_faces += 1
            if box_faces == 0:
                cv.putText(frame, "No face detected ", 
                        (top_left_x, top_left_y + int(height * 0.08)),
                        cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            elif box_faces == 1:
                single_face_inside_the_box = True
                cv.putText(frame, "Single face detected inside the box", 
                        (top_left_x, top_left_y + int(height * 0.08)),
                        cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv.putText(frame, f"{box_faces} faces detected inside the box", 
                        (top_left_x, top_left_y + int(height * 0.08)),
                        cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv.putText(frame, "No face detected", 
                    (top_left_x, top_left_y + int(height * 0.08)),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        try:
            frame, detection_result=object_detector.detect_and_draw(frame)
        except Exception as e:
            print(f"[Error] in the detecting objects: {e}")
            detection_result=None
        if detection_result and detection_result.detections:
            for detection in detection_result.detections:
                label = detection.categories[0].category_name
                if label in cheating_materials:
                    cheating_material_inside_the_box=True
                    cv.putText(frame, f"{label.capitalize()} detected inside the box",
                            (top_left_x, top_left_y + int(height * 0.15)),
                        cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    except Exception as e:
        print(f"[Critical Error] Camera function failed: {e}")
        return frame, 0, False, False, None
    return frame, box_faces, single_face_inside_the_box, cheating_material_inside_the_box, label

def initialise_camera(width=640, height=480, fps=60):
    """Initializes the camera with the specified settings."""
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv.CAP_PROP_FPS, fps)
    if not cap.isOpened():
        print("Error: Camera could not be accessed.")
        return False, None
    return True, cap
    
if __name__=="__main__":
    import cv2 as cv
    from FacePreprocessing import Facepreprocessing
    from objectDetection import ObjectDetectionModule
    model_path = r"C:\\Users\\Deepak\\OneDrive\\Desktop\\3rd year college Industry project\\Proctoring(Self)\\student_verification\\efficientdet.tflite"
    object_detector = ObjectDetectionModule(model_path=model_path)
    face_preprocessor = Facepreprocessing()
    cond, cap=initialise_camera()
    if cond==True:
        with face_preprocessor.mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Failed to read from camera.")
                    break
                frame, box_faces, single_face_inside_the_box, cheating_material_inside_the_box, label= CameraLite(frame, face_detection, object_detector)
                cv.imshow("Camera", frame)
                key=cv.waitKey(1)
                if key==13:
                    cv.imwrite("image1.jpg", frame)
                    cv.imshow('Camera', frame)
                    break
                elif key==27:
                    print("Existing")
                    break
    cap.release()
    cv.destroyAllWindows()