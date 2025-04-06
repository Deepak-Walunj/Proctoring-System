from deepface import DeepFace
import numpy as np
class StudentVerification:
    def __init__(self):
        self.modelStatus=False
        self.verifToast=""
        self.result=None
    
    def verifyStudent(self, image1, image2):
        try:
            image_1=np.array(image1)
            image_2=np.array(image2)
            self.result=DeepFace.verify(img1_path=image_1, img2_path=image_2, model_name="SFace", threshold=0.5)
            self.modelStatus=True
            self.verifToast="Verification model ran successfully"
            return self.result, self.modelStatus, self.verifToast
        except Exception as e:
            print(f"[Error] in verification model! :{e}")
            self.verifToast=f"[Error] in verification model! :{e}"
            self.modelStatus=False
            return self.result, self.modelStatus, self.verifToast
        
if __name__ == "__main__":
    studentVerificationObj=StudentVerification()
    image1=None
    image2=None
    result, verifStatus, verifToast=studentVerificationObj.verifyStudent(image1, image2)
    print(f"Result: {result}, Status: {verifStatus}, Toast: {verifToast}")