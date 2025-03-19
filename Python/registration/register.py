import cv2 as cv
import io
import sys
import os
from PIL import Image
import pymongo as py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from registration.Camera import finalImage
from detection_classes.FacePreprocessing import FacePreprocessing
from detection_classes.objectDetection import ObjectDetectionModule

client=py.MongoClient("mongodb://localhost:27017/")
db=client["CandidateFace"]
coll=db["Faces"]

def register(name):
    try:
        object_detector = ObjectDetectionModule()
        face_preprocessor = FacePreprocessing()
        cond, align_image=finalImage(object_detector, face_preprocessor)
        if cond==True:
            _, buffer = cv.imencode('.jpg', align_image)
            image_byte = io.BytesIO(buffer)
            im = Image.open(image_byte)
            image_byte = io.BytesIO()
            im.save(image_byte, format='PNG')
            doc = {
                "name": name,
                "data": image_byte.getvalue()
            }
            doc_id = coll.insert_one(doc).inserted_id
            print("Face registered successfully.")
            client.close()
            return doc_id
        else:
            return None
    except Exception as e:
        print(e)
        print("Face registeration unsuccessfull! Try again")
        return None
    finally:
        client.close()
        
if __name__ == "__main__":
    name=input("Enter your name for registeration! ")
    cond=register(name)
    print(cond)
