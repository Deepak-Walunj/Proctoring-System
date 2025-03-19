import cv2 as cv
import base64
import sys, os
from PIL import Image
import numpy as np
import pymongo
from io import BytesIO
from deepface import DeepFace
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from registration.Camera import finalImage
from detection_classes.FacePreprocessing import FacePreprocessing
from detection_classes.objectDetection import ObjectDetectionModule
from starting_viva.camera2 import Proctor

client=pymongo.MongoClient("mongodb://localhost:27017/")
db=client["CandidateFace"]
coll=db["Faces"]

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
    try:
        data=coll.find_one({"name": name}, {"_id":0, "data": 1})
        dbIstatus=False
        dbItoast=""
        if data is not None:
            image_data=data["data"]
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
            # print(image)
            pil_image = Image.open(BytesIO(image_data))
            print("From student verification, image taken from the database successfully!")
            dbItoast="From student verification, image taken from the database successfully"
            dbIstatus=True
            return pil_image, dbIstatus, dbItoast
        else:
            print("Couldn't find the student!")
            dbItoast="Couldn't find the student!"
            dbIstatus=False
            return None, dbIstatus, dbItoast
    except Exception as e:
        print(f"[Error] retrieving image from database: {e}")
        dbIstatus=False
        dbItoast=f"[Error] retrieving image from database: {e}"
        return None, dbIstatus, dbItoast
    
def faceMatching(image1, image2):
    verifToast=""
    modelStatus=False
    try:
        image_1=np.array(image1)
        image_2=np.array(image2)
        result=DeepFace.verify(img1_path=image_1, img2_path=image_2, model_name="Facenet512", threshold=0.5)
        modelStatus=True
        verifToast="Verification model ran successfully"
        return result, modelStatus, verifToast
    except Exception as e:
        print(f"[Error] in verification model! :{e}")
        verifToast=f"[Error] in verification model! :{e}"
        modelStatus=False
        return None, modelStatus, verifToast
    
def studentVerification(name):
    image1, dbIstatus, dbItoast=take_photo_from_database(name)
    if image1:
        image2, photoIstatus, photoItoast=take_photo_for_verification()
        if image2:
            result, verifStatus, verifToast=faceMatching(image1,image2)
            return result, verifStatus, verifToast
        else:
            return result, verifStatus, verifToast
    else:
        return result, verifStatus, verifToast
    
def main():
    name=input("Enter your name: ")
    result, verifStatus, verifToast=studentVerification(name)
    if verifStatus==True:
        print(f"{verifToast}")
        print(result.get("verified"))
    else:
        print(f"Not able to verify student: {verifToast}")
if __name__ == "__main__":
    main()
    
    
    