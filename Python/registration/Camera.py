import cv2 as cv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from detection_classes.FacePreprocessing import FacePreprocessing
from detection_classes.objectDetection import ObjectDetectionModule

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

capture_image = False
# Mouse callback function
def mouse_callback(event, x, y, flags, param):
    global capture_image
    if event == cv.EVENT_LBUTTONDOWN:  # Check for left mouse button click
        capture_image = True  # Set flag to capture the image

def main(object_detector, face_preprocessor, cap):
    global capture_image
    cv.namedWindow("Camera")
    cv.setMouseCallback("Camera", mouse_callback)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            frame = cv.flip(frame, 1)
            if not ret:
                print("Failed to read from camera.")
                break
            clean_frame= frame.copy()
            faceDetection_status, result_faceDetection, fDetection_toast=face_preprocessor.faceDetection(frame)
            if not faceDetection_status:
                print(fDetection_toast)
                exit()
            facePoint_status, result_facePoints, mDetection_toast=face_preprocessor.faceMesh(frame)
            if not facePoint_status:
                print(mDetection_toast)
                exit()
            frame, looking_straight_status, gaze_toast, gaze_result=face_preprocessor.gaze(frame, result_facePoints)
            frame, minDistance_status, maxDistance_status, inRange_status, distance, minD_toast=face_preprocessor.minDistance(clean_frame, result_faceDetection)
            frame, singleFace_status, box_faces, non_box_faces, singleF_toast= face_preprocessor.singleFaceInsideBox(frame, result_faceDetection)
            frame, cheating_status, object_count, objectDetectionToast=object_detector.detect_cheating(clean_frame)
            cv.imshow("Camera", frame)
            font_scale = 0.5  
            thickness = 2
            height, width, _ = frame.shape
            bottom_right_x, bottom_right_y = int(width * 0.0), int(height * 0.9)
            cv.imshow("Camera", frame)
            key = cv.waitKey(1)
            if key == 27:  # ESC
                print("Exiting...")
                cap.release()
                cv.destroyAllWindows()
                return False, None, "Program exited"
            elif key == 13 or capture_image:
                capture_image=False
                if singleFace_status and box_faces==1 and not cheating_status and inRange_status and looking_straight_status:
                    cv.putText(frame, "Face Captured", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                    print("Size of the taken image:", clean_frame.shape)
                    
                    cropFace_status, cropped_face, cropF_toast=face_preprocessor.crop_face(clean_frame, result_faceDetection)
                    if cropFace_status==False:
                        print(cropF_toast)
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, cropF_toast
                    else:
                        print(cropF_toast)
                    
                    detectLandmarks_status, tobe_align_face, count_final_landmarks, left_eye_landmark, right_eye_landmark, landmark_toast=face_preprocessor.detect_landmarks(cropped_face, result_facePoints)
                    if detectLandmarks_status==False:
                        print(landmark_toast)
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, landmark_toast
                    elif left_eye_landmark is  None or right_eye_landmark is None:
                        landmark_toast="Not able to find the eyes landmarks! Something is obstructing!"
                        print(landmark_toast)
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, landmark_toast
                    elif count_final_landmarks <468:
                        landmark_toast="Not enough landmarks detected! Please try again"
                        print(landmark_toast)
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, landmark_toast
                    else:
                        print(landmark_toast)
                    alignFace_status, final_align_face, fAlign_toast=face_preprocessor.align_face(tobe_align_face, left_eye_landmark, right_eye_landmark)
                    if alignFace_status==False:
                        print(fAlign_toast)
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, fAlign_toast
                    else:
                        print(fAlign_toast)
                        cap.release()
                        cv.destroyAllWindows()
                        return True, final_align_face, fAlign_toast
                elif not looking_straight_status:
                    cv.putText(frame, gaze_toast, 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif not singleFace_status and box_faces>1 and non_box_faces>1 and not cheating_status:
                    cv.putText(frame, "multiple faces detected", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif not singleFace_status and box_faces<1 and not cheating_status:
                    cv.putText(frame, "No face detected", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif cheating_status and singleFace_status and box_faces==1 and inRange_status:
                    cv.putText(frame, f"{objectDetectionToast}", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif singleFace_status and not inRange_status and not cheating_status:
                    cv.putText(frame, f"Distance: {int(distance)} cm", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
    except Exception as e:
        print(f"[ERROR] unable to process frames: {e}")
        toast=f"[ERROR] unable to process frames: {e}"
        cap.release()
        cv.destroyAllWindows()
        return False, None, toast
    finally:
        cap.release()
        cv.destroyAllWindows()

def finalImage(object_detector, face_preprocessor):
    # object_detector = ObjectDetectionModule()
    # face_preprocessor = FacePreprocessing()
    camStart_status, cam, cam_toast = initialize_camera()
    print(cam_toast)
    if camStart_status==True:
        print("Successfully initialised the camera!")
        condF, final_image, toast = main(object_detector, face_preprocessor, cam)
        print(toast)
        if condF==True:
            # cv.imwrite("resultImages/final.jpg", final_image)
            # cv.imshow("Camera", final_image)
            # print("Image saved as final.jpg")
            print(f"Successfully image is taken, processed and now ready to store or compare")
            return condF, final_image
        else:
            print(f"Not able to capture and process the image")
            return condF, None
    else:
        print("Camera not initialized properly!")
    return condF, None
if __name__ == "__main__":
    object_detector = ObjectDetectionModule()
    face_preprocessor = FacePreprocessing()
    finalImage(object_detector, face_preprocessor)


