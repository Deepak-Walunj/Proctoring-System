from deepface import DeepFace
import numpy as np
import cv2 as cv

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
            self.result=DeepFace.verify(img1_path=image_1, img2_path=image_2, model_name="SFace", threshold=0.5)
            self.modelStatus=True
            self.verifToast="Verification model ran successfully"
            if self.modelStatus:
                if self.result.get("verified"):
                    self.faceVerifyResult["verified"] += 1
                    print("✅ Student verified!")
                    return self.faceVerifyResult, self.modelStatus, "Student verified successfully 🎓"
                else:
                    self.faceVerifyResult["notVerified"] += 1
                    print("❌ Student not verified.")
                    return self.faceVerifyResult, self.modelStatus, "Unverified student 🚫"
            else:
                self.faceVerifyResult["Error"] += 1
                print(f"⚠️ Verification failed: {self.verifToast}")
                return None, self.modelStatus, self.verifToast
        except Exception as e:
            print(f"[Error] in verification model! :{e}")
            self.verifToast=f"[Error] in verification model! :{e}"
            self.modelStatus=False
            return self.result, self.modelStatus, self.verifToast
        
if __name__ == "__main__":
    studentVerificationObj=StudentVerification()
    image1 = r"C:\\Users\\Deepak\\OneDrive\\Desktop\\Proctoring\\Python\\testImages\\face1.jpg"
    image2 = r"C:\\Users\\Deepak\\OneDrive\\Desktop\\Proctoring\\PYTHON\\testImages\\face2.jpg"
    # img=Image.open(image1)
    # img.show()
    result, verifStatus, verifToast=studentVerificationObj.verifyStudent(image1, image2)
    print(f"Result: {result}, Status: {verifStatus}, Toast: {verifToast}")