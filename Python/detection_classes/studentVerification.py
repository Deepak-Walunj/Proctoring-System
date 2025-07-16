from deepface import DeepFace
import numpy as np
import cv2 as cv
from helperFunctions import crop_face, align_face, detect_landmarks, faceDetection, faceMesh

class StudentVerification:
    def __init__(self):
        self.modelStatus=False
        self.verifToast=""
        self.result=None
        self.faceVerifyResult = {"verified": 0, "notVerified": 0, "Error": 0}
    
    def verifyStudent(self, image1, image2):
        try:
            if isinstance(image1, str):
                image_1=cv.imread(image1)
            else:
                image_1=np.array(image1)
            if isinstance(image2, str):
                image_2=cv.imread(image2)
            else:
                image_2=np.array(image2)
            faceDetectionResponse=faceDetection(image_2)
            if not faceDetectionResponse["status"]:
                print(faceDetectionResponse["toast"])
                return {
                    "status": False,
                    "message": "Face detection failed",
                    "toast": faceDetectionResponse["toast"],
                    "result": self.faceVerifyResult,
                }
            faceMeshResponse=faceMesh(image_2)
            if not faceMeshResponse["status"]:
                print(faceMeshResponse["toast"])
                return {
                    "status": False,
                    "message": "Face mesh detection failed",
                    "toast": faceMeshResponse["toast"],
                    "result": self.faceVerifyResult,
                }
            cropResult=crop_face(image_2, faceDetectionResponse["result"])
            if not cropResult["cropFaceStatus"]:
                print(cropResult["toast"])
                return {
                    "status": False,
                    "message": "Face cropping failed",
                    "toast": cropResult["toast"],
                    "result": self.faceVerifyResult,
                }
            landmarkResult=detect_landmarks(cropResult["frame"], faceMeshResponse["result"])
            if not landmarkResult["detectLandmarksStatus"]:
                print(landmarkResult["toast"])
                return {
                    "status": False,
                    "message": "Landmark detection failed",
                    "toast": landmarkResult["toast"],
                    "result": self.faceVerifyResult,
                }
            alignResult=align_face(landmarkResult["frame"], landmarkResult["leftEyeLandmarks"], landmarkResult["rightEyeLandmarks"])
            if not alignResult["alignFaceStatus"]:
                print(alignResult["toast"])
                return {
                    "status": False,
                    "message": "Face alignment failed",
                    "toast": alignResult["toast"],
                    "result": self.faceVerifyResult,
                }
            self.result=DeepFace.verify(img1_path=image_1, img2_path=alignResult["frame"], model_name="SFace", threshold=0.5, enforce_detection=False)
            self.modelStatus=True
            self.verifToast="Verification model ran successfully"
            if self.modelStatus:
                if self.result.get("verified"):
                    self.faceVerifyResult["verified"] += 1
                    toast="✅ Student verified!"
                    
                else:
                    self.faceVerifyResult["notVerified"] += 1
                    toast="❌ Student not verified."
            else:
                self.faceVerifyResult["Error"] += 1
                self.verifToast="Error in verification model"
                toast=f"⚠️ Verification failed: "
            return {
                        "status": self.modelStatus,
                        "message":self.verifToast,
                        "toast": toast,
                        "result": self.faceVerifyResult,
                    }
        except Exception as e:
            toast=f"[Error] in verification model! :{e}"
            self.verifToast=f"[Error] in verification model! :{e}"
            self.modelStatus=False
            return {
                        "status": self.modelStatus,
                        "message":self.verifToast,
                        "toast": toast,
                        "result": self.faceVerifyResult,
                    }
        
if __name__ == "__main__":
    studentVerificationObj=StudentVerification()
    image1 = r"C:\\Users\\Deepak\\OneDrive\\Desktop\\Proctoring\\Python\\testImages\\face1.jpg"
    image2 = r"C:\\Users\\Deepak\\OneDrive\\Desktop\\Proctoring\\PYTHON\\testImages\\face1.jpg"
    # img=Image.open(image1)
    # img.show()
    response =studentVerificationObj.verifyStudent(image1, image2)
    print(f"Result: {response['result']}, Status: {response['status']}, Toast: {response['toast']}")
