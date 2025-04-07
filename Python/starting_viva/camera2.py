import cv2 as cv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from detection_classes.facePreprocessing import FacePreprocessing
from detection_classes.objectDetection import ObjectDetectionModule
from detection_classes.studentVerification import StudentVerification
from detection_classes.centralisedDatabaseOps import DatabaseOps
import time
import threading
import queue

stop_event=threading.Event()
verification_queue = queue.LifoQueue(maxsize=1)
result_queue=queue.Queue()

def run_periodic_verification(name, student_verificator, dbOps):
    verifyResult={
        "verified":0,
        "notVerified":0,
        "Error":0
    }
    while not stop_event.is_set():
        time.sleep(10) 
        if stop_event.is_set():
            print(f"Breaking the threaded event by pressing esc/enter")
            break
        pil_image1, dbIstatus, dbItoast=dbOps.take_photo_from_database(name)
        print(f"Image retrieved from database status :{dbIstatus}")
        print(f"Image retrieved from database toast :{dbItoast}")
        if not verification_queue.empty():
            frame = verification_queue.get()
            result, modelStatus, verifToast=student_verificator.verifyStudent(pil_image1, frame)
            print(f"Model run status status :{modelStatus}")
            print(f"Student verification toast :{verifToast}")
            if modelStatus:
                if result.get("verified")==True:
                    print("Student verified!")
                    verifyResult["verified"]+=1
                else:
                    print("Anonymous student!")
                    verifyResult["notVerified"]+=1
            else:
                print(f"[ERROR] model error: {verifToast}")
                verifyResult["Error"]+=1
            verification_queue.task_done()
    result_queue.put(verifyResult)
    
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

def main(object_detector, face_preprocessor, student_verificator, dbOps, cap, name):
    pStatus=False
    pToast=""
    first_frame=None
    frame_counter=0
    start_time=time.time()
    verification_thread = threading.Thread(target=run_periodic_verification, args=(name, student_verificator, dbOps,), daemon=True)
    verification_thread.start()
    try:
        while  cap.isOpened():
            start_time1=time.time()
            _, frame=cap.read()
            frame = cv.flip(frame, 1)
            clean_frame=frame.copy()            
            pStatus=True
            pToast="Proctoring started successfully!"
            faceDetection_status, result_faceDetection, fDetection_toast=face_preprocessor.faceDetection(frame)
            if not faceDetection_status:
                print(fDetection_toast)
                exit()
            facePoint_status, result_facePoints, mDetection_toast=face_preprocessor.faceMesh(frame)
            if not facePoint_status:
                print(mDetection_toast)
                exit()
            frame, looking_straight_status, gaze_toast, gazeResult=face_preprocessor.gaze(frame, result_facePoints)
            frame, minDistance_status, maxDistance_status, inRange_status, distance, minD_toast=face_preprocessor.minDistance(clean_frame, result_faceDetection)
            faceDetectionResult, toast = face_preprocessor.detectFaces(clean_frame, result_faceDetection)
            frame, cheatingMaterial_status, objectDetectionResult, objectDetectionToast = object_detector.detect_cheating(clean_frame)
            if frame_counter % 100==0:
                first_frame = clean_frame.copy()
                # print(f"Frame counter: {frame_counter}")
            frame_counter += 1
            elapsed_verification_time = time.time() - start_time
            if elapsed_verification_time >= 10:
                if first_frame is not None:
                    while not verification_queue.empty():
                        verification_queue.get_nowait()
                    verification_queue.put(first_frame)
                start_time = time.time()
                frame_counter = 0
            cv.imshow("Camera", frame)
            key=cv.waitKey(1)
            elapsed_time = time.time() - start_time1
            sleep_time = max(0, 0.1 - elapsed_time)
            time.sleep(sleep_time)
            if key == 27 or key==13:
                ptoast="Proctoring ended by pressing esc/ enter"
                stop_event.set()
                verificationResult = result_queue.get()
                print(faceDetectionResult)
                # print(verificationResult)
                # print(gazeResult)
                # print(objectDetectionResult)
                cap.release()
                cv.destroyAllWindows()
                return  pStatus, ptoast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast, verificationResult
    except Exception as e:
        pStatus=False
        print(f"[ERROR] during proctoring : {e}")
        pToast="[ERROR] during proctoring"
        return pStatus, pToast
    finally:
        stop_event.set()
        cap.release()
        cv.destroyAllWindows()

def Proctor(name):
    object_detector = ObjectDetectionModule()
    face_preprocessor = FacePreprocessing()
    student_verificator = StudentVerification()
    dbOps=DatabaseOps()
    camStart_status, cam, cam_toast = initialize_camera()
    print(cam_toast)
    if camStart_status==True:
        print(f"{cam_toast}")
        pStatus, pToast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast, verificationResult = main(object_detector, face_preprocessor, student_verificator, dbOps, cam, name)
        stop_event.set()
        return pStatus, pToast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast, verificationResult
    else:
        print("Camera not initialized properly!")
    return pStatus, pToast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast, verificationResult
if __name__ == "__main__":
    name=input("Enter your name before starting the test: ")
    pStatus, pToast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast, verificationResult= Proctor(name)
    print(f"Proctoring ended with status: {pStatus} and toast: {pToast}")
    print(f"Gaze result: {gazeResult}")
    print(f"Object Detection result: {objectDetectionResult}")
    print(f"Student verification result: {verificationResult}")
    


