from deepface import DeepFace
import cv2 as cv
import mediapipe as mp
import numpy as np


mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.7, min_tracking_confidence=0.5)

def faceDetection( frame):
    try:
        rgb_frame=cv.cvtColor(frame,cv.COLOR_BGR2RGB)
        result_detection=face_detection.process(rgb_frame)
        toast="Face detection system initialised successfully"
        return {
            "status": True,
            "message": "Face detection system initialised successfully",
            "result": result_detection
        }
    except Exception as e:
        print(f"[ERROR] detecting face: {e}")
        return {
        "status": False,
        "message": "Error in face detecting system",
        "result": None
    }

def faceMesh( frame):
    try:
        result_facePoints=face_mesh.process(frame)
        return {
            "status": True,
            "message": "Face Mesh system initialised successfully",
            "result": result_facePoints
        }
    except Exception as e:
        print(f"[ERROR] detecting face points: {e}")
        return {
            "status": False,
            "message": "Error in face mesh detecting system",
            "result": None
        }

def draw_dynamic_box(frame):
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

#Function used while registration only
def singleFaceInsideBox(face, result_faceDetection):
    toast=""
    font_scale = 0.5  
    thickness = 2
    height, width, _ = face.shape
    box_coords = (int(width * 0.3), int(height * 0.2), int(width * 0.4), int(height * 0.6))
    top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
    draw_dynamic_box(face)
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
    return {
            "status": True,
            "message": "singleFaceInsideBox function executed successfully",
            "singleFaceStatus": single_face_status,
            "boxFaces": box_faces,
            "nonBoxFaces": non_box_faces,
            "toast": toast,
            "frame": face,
        }

def crop_face(face, result_faceDetection):
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
        return {
            "status": True,
            "message": "Face cropped successfully",
            "cropFaceStatus": cropFace_status,
            "toast": toast,
            "frame": cropped_face
        }
    except Exception as e:
        print(f"[Error] in cropping the face: {e}")
        toast="Error in cropping system"
        return {
            "status": False,
            "message": "Error in cropping the face",
            "cropFaceStatus": cropFace_status,
            "toast": toast,
            "frame": face
        }
    
def detect_landmarks(face, result_facePoints):
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
            return {
                "status": True,
                "message": "Landmarks detected successfully",
                "detectLandmarksStatus": detectLandmarks_status,
                "countLandmarks": count_landmarks,
                "leftEyeLandmarks": left_eye_landmarks,
                "rightEyeLandmarks": right_eye_landmarks,
                "toast": toast,
                "frame": clean_face
            } 
        else:
            print("No landmarks found! Please clear the obstacles and try again")
            toast="No landmarks found"
            return {
                "status": True,
                "message": "No landmarks found",
                "detectLandmarksStatus": detectLandmarks_status,
                "countLandmarks": None,
                "leftEyeLandmarks": None,
                "rightEyeLandmarks": None,
                "toast": toast,
                "frame": clean_face
            } 
    except Exception as e:
        print(f"[Error] occurred while detecting face landmarks: {e}")
        toast="Error in landmark detection"
        return {
            "status": False,
            "message": "Unsuccessful in detecting landmarks",
            "detectLandmarksStatus": detectLandmarks_status,
            "countLandmarks": None,
            "leftEyeLandmarks": None,
            "rightEyeLandmarks": None,
            "toast": toast,
            "frame": clean_face
        }

def align_face(face, left_eye_landmarks, right_eye_landmarks):
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
        return {
            "status": True,
            "message": "Face aligned successfully",
            "alignFaceStatus": alignFace_status,
            "frame": aligned_face,
            "toast": toast,
        } 
    except Exception as e:
        print(f"[Error] during face alignment: {e}")
        toast="Error in aligning system"
        return {
            "status": False,
            "message": "Face alignment failed",
            "alignFaceStatus": alignFace_status,
            "frame": None,
            "toast": toast,
        }