import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from starting_viva.camera2 import Proctor

def liveProctoring(name):
    try:
        pStatus, pToast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast, verificationResult=Proctor(name)
        print(f"Proctoring ended with status: {pStatus} and toast: {pToast}")
        print(f"Gaze result: {gazeResult}")
        print(f"Object Detection result: {objectDetectionResult}")
        print(f"Student verification result: {verificationResult}")
        return pStatus, pToast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast, verificationResult
    except Exception as e:
        print(e)
        print("Proctoring Failed!")
        return False, None, None, None, None, None, None
if __name__ == "__main__":
    print("We are about to start the proctoring")
    name=input("Enter your name ")
    pStatus, pToast, gazeResult, objectDetectionResult, gaze_toast, objectDetectionToast, verificationResult=liveProctoring(name)
    print(pStatus)
