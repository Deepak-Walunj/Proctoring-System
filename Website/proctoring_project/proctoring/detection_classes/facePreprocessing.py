import cv2 as cv
import numpy as np
import mediapipe as mp
import time

class FacePreprocessing:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.7)
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.threshold_distance = 25
        self.max_threshold_distance = 35
        self.x = 0  # X-axis head pose
        self.y = 0  # Y-axis head pose
        self.X_AXIS_CHEAT = 0
        self.Y_AXIS_CHEAT = 0
        self.faceDetectionResult={
                "single":False,
                "multiple":False,
                "no":True
                }
        self.gaze_result = {
                    "Left": 0,
                    "Right": 0,
                    "Up": 0,
                    "Down": 0,
                    "Obstruct": 0,
                    "forward":0
                }
        self.prev_gaze="Forward"
        self.gaze_locked = False
        self.gaze_tracking=dict()
        
    def faceDetection(self, frame):
        faceDetection_status=False
        toast=""
        try:
            rgb_frame=cv.cvtColor(frame,cv.COLOR_BGR2RGB)
            result_detection=self.face_detection.process(rgb_frame)
            faceDetection_status=True
            toast="Face detection system initialised successfully"
        except Exception as e:
            print(f"[ERROR] detecting face: {e}")
            toast="Error in face detecting system"
            result_detection=None
        
        return faceDetection_status, result_detection, toast
    
    def faceMesh(self, frame):
        facePoint_status=False
        toast=""
        try:
            result_facePoints=self.face_mesh.process(frame)
            facePoint_status=True
            toast="Face Mesh system initialised successfully"
        except Exception as e:
            print(f"[ERROR] detecting face points: {e}")
            result_facePoints=None
            toast="Error in face mesh detecting system"
        return facePoint_status, result_facePoints, toast
    
    def draw_dynamic_box(self,frame):
        try:
            height, width, _ = frame.shape
            box_coords = (int(width * 0.3), int(height * 0.2), int(width * 0.4), int(height * 0.6))
            top_x, top_y = int(width * 0.05), int(height * 0.05)
            font_scale=0.5
            thickness=2
            box_x, box_y, box_w, box_h = box_coords
            cv.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 0, 255), 2)
            cv.putText(frame, "Press 'ENTER' to capture photo when your face is inside the box",
                    (top_x,top_y), cv.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
            cv.putText(frame, "Press 'ESC' to quit",
                    (top_x,top_y+ int(height * 0.04)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
        except Exception as e:
            print(f"[ERROR] drawing the central bounding box :{e}")
            exit()
        
    def gaze(self, face, result_facePoint):
        toast = ""
        font_scale = 0.5  
        thickness = 2
        height, width, _ = face.shape
        top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
        face_ids = [33, 263, 1, 61, 291, 199]
        gaze_status = False
        text = None
        face.flags.writeable = True
        img_h, img_w, _ = face.shape
        face_3d = []
        face_2d = []
        try:
            if result_facePoint.multi_face_landmarks:
                for face_landmarks in result_facePoint.multi_face_landmarks:
                    for idx, lm in enumerate(face_landmarks.landmark):
                        if idx in face_ids:
                            if idx == 1:
                                nose_2d = (lm.x * img_w, lm.y * img_h)
                                nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 8000)
                            x, y = int(lm.x * img_w), int(lm.y * img_h)
                            face_2d.append([x, y])
                            face_3d.append([x, y, lm.z])
                    
                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)
                    focal_length = 1 * img_w
                    cam_matrix = np.array([
                        [focal_length, 0, img_h / 2],
                        [0, focal_length, img_w / 2],
                        [0, 0, 1],
                    ])
                    dist_matrix = np.zeros((4, 1), dtype=np.float64)
                    _, rot_vec, trans_vec = cv.solvePnP(
                        face_3d, face_2d, cam_matrix, dist_matrix
                    )
                    rmat, _ = cv.Rodrigues(rot_vec)
                    angles, _, _, _, _, _ = cv.RQDecomp3x3(rmat)
                    self.x = angles[0] * 360
                    self.y = angles[1] * 360
                    
                    curr_gaze = None
                    if self.y < -10:
                        text = "Looking left? Look forward!"
                        curr_gaze = "Left"
                    elif self.y > 10:
                        text = "Looking right? Look forward!"
                        curr_gaze = "Right"
                    elif self.x < -10:
                        text = "Looking down? Look forward!"
                        curr_gaze = "Down"
                    elif self.x > 10:
                        text = "Looking up? Look forward!"
                        curr_gaze = "Up"
                    else:
                        text = "Looking forward"
                        curr_gaze = "forward"
                    gaze_status=True
                    cv.putText(face, text, (top_left_x, top_left_y + int(height * 0.18)), 
                            cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    # Implement 20-frame tracking logic
                    detected_labels = {curr_gaze}
                    for gaze in detected_labels:
                        if gaze in self.gaze_tracking:
                            self.gaze_tracking[gaze] = (self.gaze_tracking[gaze][0] + 1, 0)  # Increment detection count, reset missing count
                        else:
                            self.gaze_tracking[gaze] = (1, 0)  # New gaze detected
                    
                    objects_to_remove = []
                    for gaze in list(self.gaze_tracking.keys()):
                        if gaze not in detected_labels:
                            self.gaze_tracking[gaze] = (self.gaze_tracking[gaze][0], self.gaze_tracking[gaze][1] + 1)  # Increment missing count
                            if self.gaze_tracking[gaze][1] > 20:  # Reset if missing for 20 frames
                                objects_to_remove.append(gaze)
                    
                    for gaze in objects_to_remove:
                        del self.gaze_tracking[gaze]
                    
                    for gaze in detected_labels:
                        if self.gaze_tracking[gaze][0] == 10:  # First detection after 20 frames
                            self.gaze_result[gaze] += 1
                    self.prev_gaze = curr_gaze
                    toast = text
                    return face, gaze_status, toast, self.gaze_result
            else:
                text = "Something is obstructing the face"
                toast = text
                cv.putText(face, text, (top_left_x, top_left_y + int(height * 0.26)), 
                        cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                detected_labels = {"Obstruct"}
                for gaze in detected_labels:
                    if gaze in self.gaze_tracking:
                        self.gaze_tracking[gaze] = (self.gaze_tracking[gaze][0] + 1, 0)  
                    else:
                        self.gaze_tracking[gaze] = (1, 0)  
                objects_to_remove = []
                for gaze in list(self.gaze_tracking.keys()):
                    if gaze not in detected_labels:
                        self.gaze_tracking[gaze] = (self.gaze_tracking[gaze][0], self.gaze_tracking[gaze][1] + 1)  
                        if self.gaze_tracking[gaze][1] > 20:  
                            objects_to_remove.append(gaze)
                
                for gaze in objects_to_remove:
                    del self.gaze_tracking[gaze]
                
                for gaze in detected_labels:
                    if self.gaze_tracking[gaze][0] == 10:  
                        self.gaze_result[gaze] += 1
                
                self.prev_gaze = "Obstruct"
                return face, gaze_status, toast, self.gaze_result

        except Exception as e:
            print(f"[ERROR] face gazing system: {e}")
            toast = "Error in face gazing system"
            return face, gaze_status, toast, self.gaze_result
    
    def singleFaceInsideBox(self, face, result_faceDetection):
        toast=""
        font_scale = 0.5  
        thickness = 2
        height, width, _ = face.shape
        box_coords = (int(width * 0.3), int(height * 0.2), int(width * 0.4), int(height * 0.6))
        top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
        self.draw_dynamic_box(face)
        single_face_status=False
        box_faces=0
        non_box_faces=0
        if result_faceDetection.detections:
            for detection in result_faceDetection.detections:
                bboxC = detection.location_data.relative_bounding_box
                x, y, w, h = (int(bboxC.xmin * width), int(bboxC.ymin * height),
                            int(bboxC.width * width), int(bboxC.height * height))
                if (box_coords[0] < x < box_coords[0] + box_coords[2] and
                        box_coords[1] < y < box_coords[1] + box_coords[3] and
                        box_coords[0] < x + w < box_coords[0] + box_coords[2] and
                        box_coords[1] < y + h < box_coords[1] + box_coords[3]):
                    box_faces += 1
                else:
                    non_box_faces += 1
            if box_faces == 0:
                toast= "Please be inside the box"
                cv.putText(face,toast, (top_left_x, top_left_y + int(height * 0.08)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
            elif box_faces == 1 and non_box_faces == 0:
                toast="Single face detected inside the box"
                single_face_status = True
                cv.putText(face, toast, (top_left_x, top_left_y + int(height * 0.08)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
            elif box_faces > 1 or non_box_faces > 0:
                toast=f"Multiple faces detected :{box_faces + non_box_faces}"
                cv.putText(face, toast, (top_left_x, top_left_y + int(height * 0.08)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
        else:
            toast= "No face detected"
            cv.putText(face, toast, (top_left_x, top_left_y + int(height * 0.08)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
        return face, single_face_status, box_faces, non_box_faces, toast
    
    def minDistance(self, face, result_faceDetection):
        toast=""
        inRange_status = False
        maxDistance_status = False
        minDistance_status = False
        font_scale = 0.5
        thickness = 2
        height, width, _ = face.shape
        top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
        warning_message = None
        closest_distance = float('inf')
        successful_run_status=False
        try:
            if result_faceDetection.detections:
                for detection in result_faceDetection.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = face.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                    face_width = w
                    distance = 5000 / face_width
                    if distance < closest_distance:
                        closest_distance = distance
                if closest_distance < self.threshold_distance:
                    warning_message = f"Too close: < {self.threshold_distance} cm"
                    cv.putText(face, warning_message,
                            (top_left_x, top_left_y + int(height * 0.12)),
                            cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    minDistance_status = False
                    inRange_status = False
                elif closest_distance > self.max_threshold_distance:
                    warning_message = f"Too Far: > {self.max_threshold_distance} cm"
                    cv.putText(face, warning_message,
                            (top_left_x, top_left_y + int(height * 0.12)),
                            cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    inRange_status = False
                    maxDistance_status = False
                else:
                    warning_message=f"Distance: {int(closest_distance)} cm"
                    cv.putText(face, warning_message,
                            (top_left_x, top_left_y + int(height * 0.12)),
                            cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
                    minDistance_status = True
                    inRange_status=True
                    maxDistance_status=True
                toast=warning_message
            successful_run_status=True
            return face, minDistance_status, maxDistance_status, inRange_status, closest_distance, toast, successful_run_status
        except Exception as e:
            print(f"[ERROR] in either detecting the face or calculating the min/max distance :{e}")
            return face, minDistance_status, maxDistance_status, inRange_status, closest_distance, toast, successful_run_status
    
    def detect_faces(self, face, result_faceDetection):
        toast=""
        faceDetected_status=False
        try:
            clean_face = face.copy()
            if result_faceDetection.detections:
                for i, detection in enumerate(result_faceDetection.detections):
                    # print(detection)
                    faces= i+1
                    # print(f"Face: {faces}")
                    # print(f"  Score: {detection.score[0]}")
                    # Print bounding box
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = face.shape
                    xmin = int(bbox.xmin * w)
                    ymin = int(bbox.ymin * h)
                    box_width = int(bbox.width * w)
                    box_height = int(bbox.height * h)
                    # Draw bounding box
                    # print("  Bounding Box:")
                    # print(f"    xmin: {bbox.xmin}")
                    # print(f"    ymin: {bbox.ymin}")
                    # print(f"    width: {bbox.width}")
                    # print(f"    height: {bbox.height}")
                    faceDetected_status=True
                toast="Face detected"
                return faceDetected_status, clean_face, faces, toast
            else:
                faceDetected_status=False
                toast="No faces detected"
                return faceDetected_status, clean_face, 0, toast
        except Exception as e:
            print(f"[Error] detecting faces: {e}")
            toast="Error in deteting faces"
            return faceDetected_status, clean_face, 0, toast
    
    def detectFaces(self, frame, result_detection):
        try:
            faceCount = len(result_detection.detections) if result_detection.detections else 0
            if faceCount == 1:
                self.faceDetectionResult = {"single": True, "multiple": False, "no": False}
                toast = "Single face detected"
            elif faceCount > 1:
                self.faceDetectionResult = {"single": False, "multiple": True, "no": False}
                toast = "Multiple faces detected"
            else:
                self.faceDetectionResult = {"single": False, "multiple": False, "no": True}
                toast = "No face detected"
            return self.faceDetectionResult, toast
        except Exception as e:
            print(f"[ERROR] while detecting faces: {e}")
            toast=f"ERROR] while detecting faces: {e}"
            return None, toast
        
    def crop_face(self,face, result_faceDetection):
        cropFace_status=False
        toast=""
        try:
            clean_face = face.copy()
            if result_faceDetection.detections:
                    for detection in result_faceDetection.detections:
                        bbox = detection.location_data.relative_bounding_box
                        h, w, _ = face.shape
                        xmin = int(bbox.xmin * w)
                        ymin = int(bbox.ymin * h)
                        box_width = int(bbox.width * w)
                        box_height = int(bbox.height * h)
                        # Draw bounding box
                        cv.rectangle(face, (xmin, ymin), (xmin + box_width, ymin + box_height), (0, 255, 0), 2)
                        # print("  Bounding Box:")
                        # print(f"    xmin: {bbox.xmin}")
                        # print(f"    ymin: {bbox.ymin}")
                        # print(f"    width: {bbox.width}")
                        # print(f"    height: {bbox.height}")
            else:
                toast="No faces detected"
                return cropFace_status, face, toast
            padding_factor = 1.3  # Increase bounding box by 20%
            padding_x = int(box_width * (padding_factor - 1) / 2)
            padding_y = int(box_height * (padding_factor - 1) / 2)
            x = max(0, xmin - padding_x)
            y = max(0, ymin - padding_y)
            xmax = min(face.shape[1], xmin + box_width + padding_x)
            ymax = min(face.shape[0], ymin + box_height + padding_y)
            cropped_face = clean_face[y:ymax, x:xmax]
            if cropped_face.size == 0 or cropped_face.shape[0] == 0 or cropped_face.shape[1] == 0:
                cropFace_status=False
                toast="Error: Cropped region is invalid due to obstacles or incorrect bounding box"
                return cropFace_status, face, toast
            # print("Cropped face successfully extracted.")
            cv.imshow("Cropped face", cropped_face)
            cv.imwrite("resultImages/Cropped image.jpg", cropped_face)
            cv.waitKey(250)
            cropFace_status=True
            toast="Face cropped successfully"
            return cropFace_status, cropped_face, toast
        except Exception as e:
            print(f"[Error] in cropping the face: {e}")
            toast="Error in cropping system"
            return cropFace_status, face, toast
        
    def detect_landmarks(self, face, result_facePoints):
        detectLandmarks_status=False
        toast=""
        try:
            clean_face=face.copy()
            h, w, _ = face.shape
            # print(h,w)
            if h != w:
                size = max(h, w)
                face = cv.resize(face, (size, size))
                h, w = size, size
            if result_facePoints.multi_face_landmarks:
                for face_landmarks in result_facePoints.multi_face_landmarks:
                    landmarks = []
                    left_eye_landmarks_raw = []
                    right_eye_landmarks_raw = []
                    # Extract relevant landmarks for both eyes
                    # Left eye landmarks (from the provided indices)
                    left_eye_landmarks_raw.extend([face_landmarks.landmark[i] for i in [468, 469, 470, 471, 472]])
                    # Right eye landmarks (from the provided indices)
                    right_eye_landmarks_raw.extend([face_landmarks.landmark[i] for i in [473, 474, 475, 476, 477]])
                    left_eye_landmarks = [(landmark.x * face.shape[1], landmark.y * face.shape[0]) for landmark in left_eye_landmarks_raw]
                    right_eye_landmarks = [(landmark.x * face.shape[1], landmark.y * face.shape[0]) for landmark in right_eye_landmarks_raw]
                    # Loop through the 468 landmarks
                    for i in range(468):
                        x_float = face_landmarks.landmark[i].x * w
                        y_float = face_landmarks.landmark[i].y * h
                        landmarks.append((x_float, y_float))
                        x_int = int(x_float)
                        y_int = int(y_float)
                        cv.circle(face, (x_int, y_int), 2, (0, 255, 0), -1) 
                    detectLandmarks_status=True
                    count_landmarks= len(landmarks)
                    toast="Successfully captured landmarks!"
                cv.imshow("Landmarked face", face,)
                cv.imwrite("resultImages/Landmark detected image.jpg", face)
                cv.waitKey(250)
                return detectLandmarks_status, clean_face, count_landmarks, left_eye_landmarks, right_eye_landmarks, toast
            else:
                print("No landmarks found! Please clear the obstacles and try again")
                toast="No landmarks found"
                return detectLandmarks_status, clean_face, None, None, None, toast
        except Exception as e:
            print(f"[Error] occurred while detecting face landmarks: {e}")
            toast="Error in landmark detection"
            return detectLandmarks_status, clean_face, None, None, None, toast

    def align_face(self, face, left_eye_landmarks, right_eye_landmarks):
        toast=""
        alignFace_status=False
        try:
            # Convert landmarks to numpy arrays for better precision
            left_eye_landmarks = np.array(left_eye_landmarks, dtype=np.float32)
            right_eye_landmarks = np.array(right_eye_landmarks, dtype=np.float32)
            # Calculate the centers of both eyes
            left_eye_center = np.mean(left_eye_landmarks, axis=0)
            right_eye_center = np.mean(right_eye_landmarks, axis=0)
            # Compute the midpoint between the eyes
            eye_center = ((left_eye_center[0] + right_eye_center[0]) / 2, 
                        (left_eye_center[1] + right_eye_center[1]) / 2)
            # Calculate the angle of rotation (clockwise)
            delta_x = right_eye_center[0] - left_eye_center[0]
            delta_y = right_eye_center[1] - left_eye_center[1]
            angle = np.degrees(np.arctan2(delta_y, delta_x))
            # Create the rotation matrix
            center = (int(eye_center[0]), int(eye_center[1]))
            rotation_matrix = cv.getRotationMatrix2D(center, angle, scale=1)
            # Apply the rotation to align the face
            aligned_face = cv.warpAffine(face, rotation_matrix, (face.shape[1], face.shape[0]), flags=cv.INTER_CUBIC)
            alignFace_status=True
            toast="Face aligned successfully"
            cv.imwrite("resultImages/align.jpg", aligned_face)
            cv.imshow("Aligned image", aligned_face)
            cv.waitKey(250)
            return alignFace_status, aligned_face, toast
        except Exception as e:
            print(f"[Error] during face alignment: {e}")
            toast="Error in aligning system"
            return alignFace_status, face, toast

def initialize_camera(width=640, height=480, fps=1):
    toast=""
    camStart_status=False
    try:
        cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv.CAP_PROP_FPS, fps)
        if not cap.isOpened():
            print("Error: Camera could not be accessed.")
            toast="Camera initialisation unsuccessful"
            return camStart_status, None, toast
        camStart_status=True
        toast="Camera initialised successfully"
        return camStart_status, cap, toast
    except Exception as e:
        print(f"[Error] while initialising the camera :{e}")
        toast="Error initialising camera"
        return camStart_status, None, toast

def main(cap, face_preprocessor):
    try:
        capture_status=False
        preprocessedImage_status=False
        while cap.isOpened():
            start_time=time.time()
            ret, frame = cap.read()
            frame = cv.flip(frame, 1)
            if not ret:
                print("Failed to read from camera.")
                break
            clean_frame= frame.copy()
            faceDetection_status, result_faceDetection, fDetection_toast=obj.faceDetection(frame)
            facePoint_status, result_facePoints, mDetection_toast=obj.faceMesh(frame)
            frame, gaze_status, gaze_toast, gResult=obj.gaze(frame, result_facePoints)
            frame, minDistance_status, maxDistance_status, inRange_status, distance, distance_toast=obj.minDistance(frame, result_faceDetection)
            print(gResult)
            multipleFaceResult, toast=obj.detectFaces(frame, result_faceDetection)
            print(multipleFaceResult)
            cv.imshow("Camera", frame)
            processed_frame, single_face_status, box_faces, non_box_faces, singleFace_toast = obj.singleFaceInsideBox(frame, result_faceDetection)
            cv.imshow("Camera", processed_frame)
            key = cv.waitKey(1)
            elapsed_time=time.time()
            sleep_time = max(0, 0.1 - elapsed_time)
            time.sleep(sleep_time)
            if key == 27:  # ESC
                print("Exiting...")
                cap.release()
                cv.destroyAllWindows()
                return capture_status,preprocessedImage_status, None
            elif key == 13 :
                capture_status=True
                faceDetected_status, detected_face, total_faces, faceDetect_toast=obj.detect_faces(clean_frame, result_faceDetection)
                cv.imshow("Face Detected", detected_face)
                cv.waitKey(1000)
                if faceDetected_status==False or total_faces==0:
                    cap.release()
                    cv.destroyAllWindows()
                    return capture_status, preprocessedImage_status,None
                elif total_faces >1:
                    print("More than one face detected! Please register/login again alone.")
                    cap.release()
                    cv.destroyAllWindows()
                    return capture_status, preprocessedImage_status, None
                else:
                    print("Size of the detected image:", detected_face.shape)
                    
                cropFace_status, cropped_face, crop_toast=obj.crop_face(detected_face, result_faceDetection)
                if cropFace_status==False:
                    cap.release()
                    cv.destroyAllWindows()
                    return capture_status,preprocessedImage_status, None
                else:
                    print("Size of the cropped image:", cropped_face.shape)
                    
                detectLandmarks_status, tobe_align_face, count_final_landmarks, left_eye_landmark, right_eye_landmark, landmark_toast=obj.detect_landmarks(cropped_face, result_facePoints)
                if detectLandmarks_status is False:
                    cap.release()
                    cv.destroyAllWindows()
                    return capture_status, preprocessedImage_status, None
                elif left_eye_landmark is  None or right_eye_landmark is None:
                    print("Not able to find the eyes landmarks! Something is obstructing!")
                    cap.release()
                    cv.destroyAllWindows()
                    return capture_status, preprocessedImage_status, None
                elif count_final_landmarks <468:
                    print("Not enough landmarks detected! Please try again.")
                    cap.release()
                    cv.destroyAllWindows()
                    return capture_status, preprocessedImage_status, None
                else:
                    print("Landmark captured successfully")
                    
                alignFace_status, final_align_face, align_toast=obj.align_face(tobe_align_face, left_eye_landmark, right_eye_landmark)
                if alignFace_status==False:
                    print("Failed to align face.")
                    cap.release()
                    cv.destroyAllWindows()
                    return capture_status, preprocessedImage_status, None
                else:
                    print("Size of the final aligned image:", final_align_face.shape)
                    preprocessedImage_status=True
                    cap.release()
                    cv.destroyAllWindows()
                    return capture_status, preprocessedImage_status, final_align_face
    except Exception as e:
        print(f"[ERROR] in face processing class :{e}")
    finally:
        cap.release()
        cv.destroyAllWindows()
        print(gResult)
        print(multipleFaceResult)

if __name__ == "__main__":
    cond, cap, cam_toast = initialize_camera()
    obj=FacePreprocessing()
    capture_status, preprocessedImage_status, aligned_image = main(cap, obj)
    if capture_status==True:
        if preprocessedImage_status==True:
            cv.imwrite("resultImages/final.jpg", aligned_image)
            print("Image saved as final.jpg")
        else:
            print("Image taken but was not able to preprocess the image!")
    else:
        print("Image not captured")