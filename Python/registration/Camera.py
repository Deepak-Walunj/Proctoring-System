import cv2 as cv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from detection_classes.facePreprocessing import FacePreprocessing
from detection_classes.objectDetection import ObjectDetectionModule
from detection_classes.helperFunctions import faceDetection, faceMesh, singleFaceInsideBox, crop_face, detect_landmarks, align_face

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
            faceDetectionResponse=faceDetection(frame)
            if not faceDetectionResponse["status"]:
                print(faceDetectionResponse["toast"])
                cap.release()
                cv.destroyAllWindows()
                return False, None, faceDetectionResponse["toast"]
            faceMeshResponse=faceMesh(clean_frame)
            if not faceMeshResponse["status"]:
                print(faceMeshResponse["toast"])
                cap.release()
                cv.destroyAllWindows()
                return False, None, faceDetectionResponse["toast"]
            gazeResult=face_preprocessor.gaze(frame, faceMeshResponse["result"])
            minDistanceResult=face_preprocessor.minDistance(gazeResult["frame"], faceDetectionResponse["result"])
            singleFaceInsideBoxResult= singleFaceInsideBox(minDistanceResult["frame"], faceDetectionResponse["result"])
            objectDetectionResult=object_detector.detect_cheating(singleFaceInsideBoxResult["frame"])
            # cv.imshow("Camera", )
            font_scale = 0.5  
            thickness = 2
            height, width, _ = frame.shape
            bottom_right_x, bottom_right_y = int(width * 0.0), int(height * 0.9)
            cv.imshow("Camera", objectDetectionResult["frame"])
            key = cv.waitKey(1)
            if key == 27:  # ESC
                print("Exiting...")
                cap.release()
                cv.destroyAllWindows()
                return False, None, "Program exited"
            elif key == 13 or capture_image:
                capture_image=False
                if singleFaceInsideBoxResult["singleFaceStatus"] and singleFaceInsideBoxResult["boxFaces"]==1 and not objectDetectionResult["cheating_material_status"] and minDistanceResult["inRange_status"] and gazeResult["looking_straight_status"]:
                    cv.putText(frame, "Face Captured", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                    print("Size of the taken image:", clean_frame.shape)
                    
                    cropResult=crop_face(clean_frame, faceDetectionResponse["result"])
                    if cropResult["cropFaceStatus"]==False:
                        print(cropResult["toast"])
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, cropResult["toast"]
                    else:
                        print(cropResult["toast"])
                    landmarkResult=detect_landmarks(cropResult["frame"], faceMeshResponse["result"])
                    if landmarkResult["detectLandmarksStatus"]==False:
                        print(landmarkResult["toast"])
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, landmarkResult["toast"]
                    elif landmarkResult["leftEyeLandmarks"] is None or landmarkResult["rightEyeLandmarks"] is None:
                        landmark_toast="Not able to find the eyes landmarks! Something is obstructing!"
                        print(landmark_toast)
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, landmarkResult["toast"]
                    elif landmarkResult["countLandmarks"] <468:
                        landmark_toast="Not enough landmarks detected! Please try again"
                        print(landmark_toast)
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, landmarkResult["toast"]
                    else:
                        print(landmarkResult["toast"])
                    alignResult=align_face(landmarkResult["frame"], landmarkResult["leftEyeLandmarks"], landmarkResult["rightEyeLandmarks"])
                    if alignResult["alignFaceStatus"]==False:
                        print(alignResult["toast"])
                        cap.release()
                        cv.destroyAllWindows()
                        return False, None, alignResult["toast"]
                    else:
                        print(alignResult["toast"])
                        cap.release()
                        cv.destroyAllWindows()
                        return True, alignResult["frame"], alignResult["toast"]
                elif not gazeResult["looking_straight_status"]:
                    cv.putText(frame, gazeResult["toast"], 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif not singleFaceInsideBoxResult["singleFaceStatus"] and singleFaceInsideBoxResult["boxFaces"]>1 and not objectDetectionResult["cheating_material_status"]:
                    cv.putText(frame, "multiple faces detected", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif not singleFaceInsideBoxResult["singleFaceStatus"] and singleFaceInsideBoxResult["boxFaces"]<1 and not objectDetectionResult["cheating_material_status"]:
                    cv.putText(frame, "No face detected", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif objectDetectionResult["cheating_material_status"] and singleFaceInsideBoxResult["singleFaceStatus"] and singleFaceInsideBoxResult["boxFaces"]==1 and minDistanceResult["inRange_status"]:
                    cv.putText(frame, f"{objectDetectionResult['toast']}", 
                        (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                    cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                elif singleFaceInsideBoxResult["singleFaceStatus"] and not minDistanceResult["inRange_status"] and not objectDetectionResult["cheating_material_status"]:
                    cv.putText(frame, f"Distance: {int(minDistanceResult['closest_distance'])} cm", 
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
    # print(cam_toast)
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
        return False, None
if __name__ == "__main__":
    object_detector = ObjectDetectionModule()
    face_preprocessor = FacePreprocessing()
    finalImage(object_detector, face_preprocessor)


