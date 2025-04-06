import cv2 as cv
import sys, os
from PIL import Image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from registration.Camera import finalImage
from detection_classes.facePreprocessing import FacePreprocessing
from detection_classes.objectDetection import ObjectDetectionModule
from detection_classes.studentVerification import StudentVerification
from detection_classes.centralisedDatabaseOps import DatabaseOps

def take_photo_for_verification():
    try:
        photoIstatus=False
        photoItoast=""
        object_detector = ObjectDetectionModule()
        face_preprocessor = FacePreprocessing()
        cond, align_image=finalImage(object_detector, face_preprocessor)
        if cond==True:
            pil_image = Image.fromarray(cv.cvtColor(align_image, cv.COLOR_BGR2RGB))
            photoItoast="Successfully take photograph for verification"
            photoIstatus=True
            return pil_image, photoIstatus, photoItoast
        else:
            photoItoast="Unsuccessfull to take a photograph for verification"
            photoIstatus=False
            return None, photoIstatus, photoItoast
    except Exception as e:
        print(f"[ERROR] while taking photo for registeration! :{e}")
        photoItoast=f"[ERROR] while taking photo for registeration! :{e}"
        photoIstatus=False
        return  None, photoIstatus, photoItoast

def take_photo_from_database(name):
    dbOps=DatabaseOps()
    pil_image, dbIstatus, dbItoast=dbOps.take_photo_from_database(name)
    print(dbItoast)
    return pil_image, dbIstatus, dbItoast

def faceMatching(image1, image2):
    studentVerificationObj=StudentVerification()
    result, verifStatus, verifToast=studentVerificationObj.verifyStudent(image1, image2)
    return result, verifStatus, verifToast
    
def verifyStudent(name):
    image1, dbIstatus, dbItoast=take_photo_from_database(name)
    if dbIstatus:
        image2, photoIstatus, photoItoast=take_photo_for_verification()
        if image2:
            result, verifStatus, verifToast=faceMatching(image1,image2)
            return result, verifStatus, verifToast
        else:
            return result, verifStatus, verifToast
    else:
        result=None
        verifStatus=False
        verifToast="Couldn't find the student!"
        return result, verifStatus, verifToast
    
def main():
    name=input("Enter your name: ")
    result, verifStatus, verifToast=verifyStudent(name)
    if verifStatus==True:
        print(f"{verifToast}")
        print(result.get("verified"))
    else:
        print(f"Not able to verify student: {verifToast}")
if __name__ == "__main__":
    main()
    
    
    