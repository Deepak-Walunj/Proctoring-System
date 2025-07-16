import cv2 as cv
import numpy as np
import time
# from helperFunctions import faceDetection, faceMesh

class FacePreprocessing:
    def __init__(self):
        self.min_threshold_distance = 25
        self.max_threshold_distance = 35
        
        self.faceDetectionResult=False
        
        self.x = 0  # X-axis head pose
        self.y = 0  # Y-axis head pose
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
        
    def gaze(self, face, result_facePoint):
        try:
            toast = ""
            font_scale = 0.5  
            thickness = 2
            height, width, _ = face.shape
            top_left_x, top_left_y = int(width * 0.05), int(height * 0.05)
            face_ids = [33, 263, 1, 61, 291, 199]
            looking_straight_status = False
            text = None
            face.flags.writeable = True
            img_h, img_w, _ = face.shape
            face_3d = []
            face_2d = []
            
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
                        looking_straight_status = True
                        curr_gaze = "forward"
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
                        if self.gaze_tracking[gaze][0] == 20:  # First detection after 20 frames
                            self.gaze_result[gaze] += 1
                    self.prev_gaze = curr_gaze
                    toast = text
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
            return {
                "status": True,
                "message": "Gaze tracking successful",
                "gaze_result": self.gaze_result,
                "toast": toast,
                "looking_straight_status": looking_straight_status,
                "frame": face
                }
        except Exception as e:
            print(f"[ERROR] face gazing system: {e}")
            toast = "Error in face gazing system"
            return {
                "status": False,
                "message": "Gaze tracking unsuccessful",
                "gaze_result": self.gaze_result,
                "toast": toast,
                "looking_straight_status": looking_straight_status,
                "frame": face
                }
    
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
                if closest_distance < self.min_threshold_distance:
                    warning_message = f"Too close: < {self.min_threshold_distance} cm"
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
            return {
                "status": True,
                "message": "Distance calculation successful",
                "minDistance_status": minDistance_status,
                "maxDistance_status": maxDistance_status,
                "inRange_status": inRange_status,
                "closest_distance": closest_distance,
                "toast": toast,
                "frame": face
            }
        except Exception as e:
            print(f"[ERROR] in either detecting the face or calculating the min/max distance :{e}")
            return{
                "status": False,
                "message": "Error in distance calculation",
                "minDistance_status": False,
                "maxDistance_status": False,
                "inRange_status": False,
                "closest_distance": None,
                "toast": None,
                "frame": face
            }
    
    def detectFaces(self, frame, result_detection):
        try:
            face_count = len(result_detection.detections) if result_detection and result_detection.detections else 0
            if face_count == 0:
                toast = "No face detected"
                faceDetection_status = False
            elif face_count == 1:
                toast = "Single face detected"
                faceDetection_status = True
            else:
                toast = f"Multiple faces detected: {face_count}"
                faceDetection_status = True
            # print(toast)
            return {
                "status": faceDetection_status,
                "face_count": face_count,
                "message": toast
            }
        except Exception as e:
            print(f"[ERROR] in detectFaces: {e}")
            return {
                "status": False,
                "face_count": 0,
                "message": "Error in face counting system"
            }
    
# def initialize_camera(width=640, height=480, fps=1):
#     toast=""
#     camStart_status=False
#     try:
#         cap = cv.VideoCapture(0, cv.CAP_DSHOW)
#         cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
#         cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
#         cap.set(cv.CAP_PROP_FPS, fps)
#         if not cap.isOpened():
#             print("Error: Camera could not be accessed.")
#             toast="Camera initialisation unsuccessful"
#             return camStart_status, None, toast
#         camStart_status=True
#         toast="Camera initialised successfully"
#         return camStart_status, cap, toast
#     except Exception as e:
#         print(f"[Error] while initialising the camera :{e}")
#         toast="Error initialising camera"
#         return camStart_status, None, toast

# def main(cap, obj1):
#     try:
#         capture_status=False
#         preprocessedImage_status=False
#         while cap.isOpened():
#             start_time=time.time()
#             ret, frame = cap.read()
#             frame = cv.flip(frame, 1)
#             if not ret:
#                 print("Failed to read from camera.")
#                 break
#             clean_frame= frame.copy()
#             faceDetectionResponse=faceDetection(frame)
#             faceMeshResponse=faceMesh(frame)
#             gazeResult=obj1.gaze(frame, faceMeshResponse['result'])
#             minDistanceResult=obj1.minDistance(gazeResult["frame"], faceDetectionResponse['result'])
#             print(gazeResult['gaze_result'])
#             faceDetectionResult=obj1.detectFaces(minDistanceResult["frame"], faceDetectionResponse['result'])
#             print(faceDetectionResult['face_count'])
#             # cv.imshow("Camera", frame)
#             # processed_frame, single_face_status, box_faces, non_box_faces, singleFace_toast = obj.singleFaceInsideBox(frame, faceDetectionResponse['result'])
#             cv.imshow("Camera", frame)
#             key = cv.waitKey(1)
#             elapsed_time=time.time()
#             sleep_time = max(0, 0.1 - elapsed_time)
#             time.sleep(sleep_time)
#             if key == 27:  # ESC
#                 print("Exiting...")
#                 cap.release()
#                 cv.destroyAllWindows()
#                 return capture_status,preprocessedImage_status, None
#             elif key == 13 :
#                 capture_status=True
#                 faceDetected_status, detected_face, total_faces, faceDetect_toast=obj1.detect_faces(clean_frame, faceDetectionResponse['result'])
#                 cv.imshow("Face Detected", detected_face)
#                 cv.waitKey(1000)
#                 if faceDetected_status==False or total_faces==0:
#                     cap.release()
#                     cv.destroyAllWindows()
#                     return capture_status, preprocessedImage_status,None
#                 elif total_faces >1:
#                     print("More than one face detected! Please register/login again alone.")
#                     cap.release()
#                     cv.destroyAllWindows()
#                     return capture_status, preprocessedImage_status, None
#                 else:
#                     print("Size of the detected image:", detected_face.shape)
                    
#                 cropFace_status, cropped_face, crop_toast=obj1.crop_face(detected_face, faceDetectionResponse['result'])
#                 if cropFace_status==False:
#                     cap.release()
#                     cv.destroyAllWindows()
#                     return capture_status,preprocessedImage_status, None
#                 else:
#                     print("Size of the cropped image:", cropped_face.shape)
                    
#                 detectLandmarks_status, tobe_align_face, count_final_landmarks, left_eye_landmark, right_eye_landmark, landmark_toast=obj1.detect_landmarks(cropped_face, faceMeshResponse['result'])
#                 if detectLandmarks_status is False:
#                     cap.release()
#                     cv.destroyAllWindows()
#                     return capture_status, preprocessedImage_status, None
#                 elif left_eye_landmark is  None or right_eye_landmark is None:
#                     print("Not able to find the eyes landmarks! Something is obstructing!")
#                     cap.release()
#                     cv.destroyAllWindows()
#                     return capture_status, preprocessedImage_status, None
#                 elif count_final_landmarks <468:
#                     print("Not enough landmarks detected! Please try again.")
#                     cap.release()
#                     cv.destroyAllWindows()
#                     return capture_status, preprocessedImage_status, None
#                 else:
#                     print("Landmark captured successfully")
                    
#                 alignFace_status, final_align_face, align_toast=obj1.align_face(tobe_align_face, left_eye_landmark, right_eye_landmark)
#                 if alignFace_status==False:
#                     print("Failed to align face.")
#                     cap.release()
#                     cv.destroyAllWindows()
#                     return capture_status, preprocessedImage_status, None
#                 else:
#                     print("Size of the final aligned image:", final_align_face.shape)
#                     preprocessedImage_status=True
#                     cap.release()
#                     cv.destroyAllWindows()
#                     return capture_status, preprocessedImage_status, final_align_face
#     except Exception as e:
#         print(f"[ERROR] in face processing class :{e}")
#         return False, False, None
#     finally:
#         cap.release()
#         cv.destroyAllWindows()
#         print(gazeResult['gaze_result'])
#         # print(faceDetectionResult["total_unique_unauthorized_faces"])

# if __name__ == "__main__":
#     cond, cap, cam_toast = initialize_camera()
#     obj1=FacePreprocessing()
#     capture_status, preprocessedImage_status, aligned_image = main(cap, obj1)
#     if capture_status==True:
#         if preprocessedImage_status==True:
#             cv.imwrite("resultImages/final.jpg", aligned_image)
#             print("Image saved as final.jpg")
#         else:
#             print("Image taken but was not able to preprocess the image!")
#     else:
#         print("Image not captured")