from FacePreprocessing import FacePreprocessing
from objectDetection import ObjectDetectionModule
from starting_viva.Camera2 import liveProctoring

# def initialize_camera(width=640, height=480, fps=1):
#     toast=""
#     camStart_status=False
#     try:
#         cap = cv.VideoCapture(0, cv.CAP_DSHOW)
#         cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
#         cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
#         cap.set(cv.CAP_PROP_FPS, fps)
#         if not cap.isOpened():
#             print("Error: Camera could not be accessed.")
#             toast="Camera initialisation unsuccessful"
#             return camStart_status, None, toast
#         camStart_status=True
#         toast="Camera initialised successfully"
#         return camStart_status, cap, toast
#     except Exception as e:
#         print(f"[Error] while initialising the camera :{e}")
#         toast="Error initialising camera"
#         return camStart_status, None, toast

# def main(cap, face_preprocessor):
#     pStatus=False
#     pToast=""
#     objectDetectionCount=0
#     faceDetectionCount=0
#     try:
#         while  cap.isOpened():
#             _, frame=cap.read()
#             proctoringStatus=True
#             pToast="Proctoring started successfully!"
#             cv.imshow("Camera", frame)
#             key=cv.waitKey(1)
#             if key == 27:
#                 ptoast="Proctoring ended by pressing esc"
#                 cap.release()
#                 cv.destroyAllWindows()
#                 return pStatus, ptoast
#             if key==13:
#                 ptoast="Proctoring ended by pressing esc"
#                 cap.release()
#                 cv.destroyAllWindows()
#                 return pStatus, ptoast
                
#     except Exception as e:
#         pToast="[ERROR] initialising the camera"
#         return pStatus, pToast
        
# def startedViva():
#     face_preprocessor=FacePreprocessing()
#     object_detector=ObjectDetectionModule()
#     camStatus, cap, cToast=initialize_camera()
#     pStatus, pToast=main(cap, face_preprocessor)
#     print(camStatus, cToast, pStatus, pToast)

# if __name__=="__main__":
#     ctoast, pStatus, pToast=startedViva()
#     print(ctoast, pStatus, pToast)

def startViva():
    face_preprocessor=FacePreprocessing()
    object_detector=ObjectDetectionModule()
    camStatus, cToast, pStatus, pToast=liveProctoring(face_preprocessor, object_detector)
    print(camStatus, cToast, pStatus, pToast)
    

if __name__=="__main__":
    ctoast, pStatus, pToast=startViva()
    print(ctoast, pStatus, pToast)