import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from registration.Camera import finalImage
from detection_classes.facePreprocessing import FacePreprocessing
from detection_classes.objectDetection import ObjectDetectionModule
from detection_classes.centralisedDatabaseOps import DatabaseOps

def register(name):
    try:
        object_detector = ObjectDetectionModule()
        face_preprocessor = FacePreprocessing()
        cond, align_image=finalImage(object_detector, face_preprocessor)
        if cond==True:
            dbOps=DatabaseOps()
            doc_id, status, toast=dbOps.registerStudent(name, align_image)
            print(toast)
            return doc_id
        else:
            return None
    except Exception as e:
        print(e)
        print("Face registeration unsuccessfull! Try again")
        return None
        
if __name__ == "__main__":
    name=input("Enter your name for registeration! ")
    cond=register(name)
    print(cond)
