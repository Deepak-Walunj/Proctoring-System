from deepface import DeepFace
import cv2 as cv
import mediapipe as mp


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
    return face, single_face_status, box_faces, non_box_faces, toast