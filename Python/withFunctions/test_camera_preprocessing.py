import cv2 as cv
import numpy as np
import mediapipe as mp
import logging
from absl import logging as absl_logging
from dotenv import load_dotenv
load_dotenv()
import warnings
import tensorflow as tf
warnings.filterwarnings("ignore")
# Disable specific MediaPipe logs
tf.get_logger().setLevel(absl_logging.ERROR)
tf.get_logger().setLevel(logging.ERROR)  # Suppress TensorFlow logs below ERROR
# Optionally suppress other logs using Python logging
logging.basicConfig(level=logging.ERROR)

capture_image = False
# Mouse callback function
def mouse_callback(event, x, y, flags, param):
    global capture_image
    if event == cv.EVENT_LBUTTONDOWN:  # Check for left mouse button click
        capture_image = True  # Set flag to capture the image

def camera(frame, mp_face_detection, font_scale, thickness, box_coords, top_left_x, top_left_y, width, height):
    with mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection:
        draw_dynamic_box(frame, box_coords, (top_left_x, top_left_y), height, font_scale, thickness)
        single_face_inside_the_box = False
        box_faces = 0
        non_box_faces = 0
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        # Process detected faces
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
            # No detections
            cv.putText(frame, "No face detected", 
                    (top_left_x, top_left_y + int(height * 0.08)),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    return frame, single_face_inside_the_box, box_faces

def initialize_camera(width=640, height=480, fps=60):
    """Initializes the camera with the specified settings."""
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv.CAP_PROP_FPS, fps)
    if not cap.isOpened():
        print("Error: Camera could not be accessed.")
        return False, None
    return True, cap

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

def detect_face_and_give_insight(face, mp_face_detection):
    try:
        clean_face=face.copy()
        with mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection:
            results = face_detection.process(face)
            if results.detections:
                for i, detection in enumerate(results.detections):
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
                    cv.rectangle(face, (xmin, ymin), (xmin + box_width, ymin + box_height), (0, 255, 0), 2)
                    # print("  Bounding Box:")
                    # print(f"    xmin: {bbox.xmin}")
                    # print(f"    ymin: {bbox.ymin}")
                    # print(f"    width: {bbox.width}")
                    # print(f"    height: {bbox.height}")
            else:
                print("No faces detected.")
                return False, None, None
            # print(f"Total number of faces detected: {faces}")
            cv.imshow("Faces Detected", face)
            cv.waitKey(0)
            padding_factor = 1.3  # Increase bounding box by 20%
            padding_x = int(box_width * (padding_factor - 1) / 2)
            padding_y = int(box_height * (padding_factor - 1) / 2)
            x = max(0, xmin - padding_x)
            y = max(0, ymin - padding_y)
            xmax = min(face.shape[1], xmin + box_width + padding_x)
            ymax = min(face.shape[0], ymin + box_height + padding_y)
            cropped_face = clean_face[y:ymax, x:xmax]
            if cropped_face.size == 0 or cropped_face.shape[0] == 0 or cropped_face.shape[1] == 0:
                    print("Error: Cropped region is invalid due to obstacles or incorrect bounding box.")
                    return False, None, faces
            print("Cropped face successfully extracted.")
            return True, cropped_face, faces
    except Exception as e:
        print(f"Error occurred while detecting face and landmarks: {e}")
        return False, None, None
    
def detect_landmarks(face, mp_face_mesh):
    try:
        clean_face=face.copy()
        h, w, _ = face.shape
        # print(h,w)
        if h != w:
            size = max(h, w)
            face = cv.resize(face, (size, size))
            h, w = size, size 
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.7, 
                                min_tracking_confidence=0.5) as face_mesh:
            input_image = cv.cvtColor(face, cv.COLOR_BGR2RGB)
            results=face_mesh.process(input_image)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                # Create a list to store the landmarks
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
                        # Draw small green dots on the landmarks
                        cv.circle(face, (x_int, y_int), 2, (0, 255, 0), -1)  # Green color, radius=2, filled circle
                    print("Successfully captured landmarks!")
                    count_landmarks= len(landmarks)
                    # print(count_landmarks)
                    return True, face, clean_face, count_landmarks, left_eye_landmarks, right_eye_landmarks
            else:
                print("No landmarks found! Please clear the obstacles and try again")
                return False, face, clean_face, None, None, None
    except Exception as e:
        print("Error occurred while aligning face: ", str(e))
        return False, face, clean_face, None, None, None

def align_face(face, left_eye_landmarks, right_eye_landmarks):
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
        return True, aligned_face
    except Exception as e:
        print(f"Error during face alignment: {e}")
        return False, face  # Return the original face if alignment fails

def finalImage():
    global capture_image
    mp_face_detection = mp.solutions.face_detection
    mp_face_mesh = mp.solutions.face_mesh
    cond, cap = initialize_camera()
    if cond==True:
        cv.namedWindow("Camera")
        cv.setMouseCallback("Camera", mouse_callback)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to read from camera.")
                break
            clean_frame= frame.copy()
            font_scale = 0.5  
            thickness = 2
            height, width, _ = frame.shape
            box_coords = (int(width * 0.3), int(height * 0.2), int(width * 0.4), int(height * 0.6))
            top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
            bottom_right_x, bottom_right_y = int(width * 0.0), int(height * 0.9)
            frame, single_face_inside_the_box, box_faces=camera(frame, mp_face_detection, font_scale, thickness, box_coords, top_left_x, top_left_y, width, height)
            cv.imshow("Camera", frame)
            key = cv.waitKey(1)
            if key == 27:  # ESC
                print("Exiting...")
                cap.release()
                cv.destroyAllWindows()
                return False, None
            elif key == 13 or capture_image:
                capture_image=False
                if  single_face_inside_the_box and box_faces==1:
                    cv.putText(frame, "Face Captured", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                    # print("Size of the freshly taken image:", clean_frame.shape)
                    cv.imshow("Fresh image", clean_frame)
                    # cv.imwrite("Fresh image.jpg", clean_frame)
                    
                    cond, cropped_face, total_faces=detect_face_and_give_insight(clean_frame, mp_face_detection)
                    if cond==False or total_faces==None:
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None
                    elif total_faces >1:
                        print("More than one face detected! Please register again alone.")
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None
                    else:
                        # print("Size of the cropped image:", cropped_face.shape)
                        cv.imshow("Cropped face", cropped_face)
                        cv.imwrite("resultImages/Cropped image.jpg", cropped_face)
                        cv.waitKey(0)
                        
                        cond, landmarked_face, tobe_align_face, count_final_landmarks, left_eye_landmark, right_eye_landmark=detect_landmarks(cropped_face, mp_face_mesh)
                        if cond is False:
                            cap.release()
                            cv.destroyAllWindows()
                            return False, None
                        elif left_eye_landmark is  None or right_eye_landmark is None:
                            print("Not able to find the eyes landmarks! Something is obstructing!")
                            cap.release()
                            cv.destroyAllWindows()
                            return False, None
                        elif count_final_landmarks <468:
                            print("Not enough landmarks detected! Please try again.")
                            cap.release()
                            cv.destroyAllWindows()
                            return False, None
                        else:
                            # print("Size of the landmarked image:", landmarked_face.shape)
                            cv.imshow("Landmarked face", landmarked_face,)
                            cv.imwrite("resultImages/Landmark detected image.jpg", landmarked_face)
                            cv.waitKey(0)
                            # print(f"Finally we got the landmarks of the face: {final_landmarks}")
                            # print("Left iris landmarks: ", left_eye_landmark)
                            # print("Right iris landmarks: ", right_eye_landmark)
                            
                            cond, final_align_face=align_face(tobe_align_face, left_eye_landmark, right_eye_landmark)
                            if cond==False:
                                print("Failed to align face.")
                                cap.release()
                                cv.destroyAllWindows()
                                return False, None
                            else:
                                # print("Size of the final aligned image:", final_align_face.shape)
                                cv.imwrite("resultImages/align.jpg", final_align_face)
                                cv.imshow("Aligned image", final_align_face)
                                cv.waitKey(0)
                                cap.release()
                                cv.destroyAllWindows()
                                return True, final_align_face
                elif not single_face_inside_the_box and box_faces>1:
                    cv.putText(frame, "multiple faces detected", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    # print("Please align your face within the box.")
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif not single_face_inside_the_box and box_faces<1:
                    cv.putText(frame, "No face detected", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    # print("Please align your face within the box.")
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
        cap.release()
        cv.destroyAllWindows()
    else:
        print("Camera not initialized properly!")
        return False, None
    return False, None

if __name__ == "__main__":
    cond, aligned_image = finalImage()
    if cond==True:
        cv.imwrite("resultImages/final.jpg", aligned_image)
        print("Image saved as final.jpg")
    else:
        print(cond)