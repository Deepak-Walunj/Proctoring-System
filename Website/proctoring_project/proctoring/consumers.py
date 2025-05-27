# import json
# import base64
# import numpy as np
# from io import BytesIO
# from PIL import Image
# from .detection_classes.facePreprocessing import FacePreprocessing
# from .detection_classes.objectDetection import ObjectDetectionModule
# from .detection_classes.centralisedDatabaseOps import DatabaseOps
# from .detection_classes.studentVerification import StudentVerification
# import cv2 as cv
# import os
# import sys
# from channels.generic.websocket import AsyncWebsocketConsumer
# import time

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

# class WebRTCConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#     async def connect(self):
#         self.object_detector = ObjectDetectionModule()
#         self.face_preprocessor = FacePreprocessing()
#         self.student_verificator = StudentVerification()
#         self.dbOps = DatabaseOps()
#         self.latest_frame = None
#         self.username = None
#         self.last_verification_time = time.time()
#         self.per_frame_result={
#                                     "fDetection_toast": "",
#                                     "facePoints_detection_toast": "",
#                                     "gaze_toast": "",
#                                     "distance_toast": {
#                                         "toast":"",
#                                         "distance": 0
#                                         },
#                                     "object_toast": "",
#                                     "student_verification_toast": "",
#                                 }
#         self.result=[]
#         self.id=0
#         self.final_toast=""
#         await self.accept()
        
#         print("WebSocket connected: Live streaming setup successfully!")
        
#     async def disconnect(self, close_code):
#         await self.send(text_data=json.dumps({
#             "type":"success",
#             "final_result": self.result
#         }))
        
#         await self.object_detector.cleanup()
#         await self.face_preprocessor.cleanup()
#         await self.student_verificator.cleanup()
#         await self.dbOps.cleanup()
#         self.per_frame_result=None
#         self.result=None
#         self.latest_frame = None
#         self.username = None
#         self.last_verification_time = None
#         self.index=None
#         self.final_toast=None
#         print("WebSocket disconnected: Streaming ended.")
        
#     async def receive(self, text_data):
#         try:
#             data = json.loads(text_data)
#             print(type(data))
#             print(f"Received signaling message: {data['type']} ")
#             print(f"Received username: {data['name']}")
            
#             if(data['type']=='frame'):
#                 base64_str = data['frame'].split(',')[1]
#                 image_data = base64.b64decode(base64_str)
#                 img = Image.open(BytesIO(image_data))
#                 frame=cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
#                 print(type(frame))
                
#                 # Ensure dtype is uint8
#                 if frame.dtype != np.uint8:
#                     frame = frame.astype(np.uint8)
#                     print("rectangle error")
#                 self.latest_frame = frame
#                 self.username = data['name']
#                 await process_frame_status, process_frame_toast=await self.process_frame(self)
#                 current_time = time.time()
#                 if current_time - self.last_verification_time >= 10:
#                     self.last_verification_time = current_time
#                     verifyStatus, verifyToast = await self.verificationStudent(self)
#                     if not verifyStatus:
#                         process_frame_status=verifyStatus 
#                         self.final_toast=process_frame_toast + "but" + verifyToast
#                 if not process_frame_status:
#                     await self.send(text_data=json.dumps({
#                         "type": "fail",
#                         "final_toast": self.final_toast
#                     }))
#                 else:
#                     self.final_toast=process_frame_toast + "and" + verifyToast
#                     await self.send(text_data=json.dumps({
#                         "type": "success",
#                         "final_toast": self.final_toast,
#                         "per_frame_result": self.per_frame_result
#                     }))
#             else:
#                 print(f"Unknown message type received: {data['type']}")
#             if data.get("type") == "offer":
#                 print("Offer received: Live streaming in progress.")
#             elif data.get("type") == "new-ice-candidate":
#                 print("ICE candidate received.")
#         except Exception as e:
#             print(f"[ERROR] failed to process frame: {e}")
    
#     async def process_frame(self):
#         print("type of frame in process frame fun is : ",type(self.latest_frame))
#         self.id+=1
#         try:
#             try:
#                 faceDetection_status, result_faceDetection, fDetection_toast=self.face_preprocessor.faceDetection(self.latest_frame)
#             except Exception as e:
#                 return False, f"faceDetection() failed: {e}"
#             try:
#                 facePoint_status, result_facePoints, facePoints_detection_toast=self.face_preprocessor.faceMesh(self.latest_frame)
#             except Exception as e:
#                 return False, f"faceMesh() failed: {e}"
#             try:
#                 frame, gaze_status, gaze_toast, gazeResult=self.face_preprocessor.gaze(self.latest_frame, result_facePoints)
#             except Exception as e:
#                 return False, f"gaze() failed: {e}"
#             try: 
#                 frame, minDistance_status, maxDistance_status, inRange_status, distance, minD_toast, min_D_successful_run_status=self.face_preprocessor.minDistance(self.latest_frame, result_faceDetection)
#             except Exception as e:
#                 return False, f"minDistance() failed: {e}"
#             try:
#                 frame, object_detection_status, object_detection_result, object_toast=self.object_detector.detect_cheating(self.latest_frame)
#             except Exception as e:
#                 return False, f"objectDetection() failed: {e}"
#             if not faceDetection_status or not facePoint_status or not gaze_status or not min_D_successful_run_status or object_detection_status:
#                 print("One or more checks failed, returning the frame without further processing.")
#                 return False, "One or more checks failed, returning the frame without further processing."
#             self.per_frame_result={
#                                     "fDetection_toast": fDetection_toast,
#                                     "facePoints_detection_toast": facePoints_detection_toast,
#                                     "gaze_toast": gaze_toast,
#                                     "distance_toast": {
#                                         "toast":minD_toast,
#                                         "distance": distance
#                                         },
#                                     "object_toast": object_toast,
#                                     "student_verification_toast": "",
#                                 }
#             self.result.append(
#                                 {
#                                     "id": self.id,
#                                     "result_faceDetection": result_faceDetection,
#                                     "result_facePoints": result_facePoints,
#                                     "gazeResult": gazeResult,
#                                     "object_detection_result": object_detection_result,
#                                 }
#                                 )
#             return True,  "Frame processed successfully!"
#         except Exception as e:
#             self.id+=1
#             self.result.append(
#                 {
#                     "id": self.id,
#                     "error": f"Frame failed due to: {e}"
#                 }
#                 )
#             return False, f"[ERROR] unable to process frames: {e}"
            
#     async def verificationStudent(self):
#         verifyToast=""
#         verifyStatus=False
#         try:
#             pil_image1, dbIstatus, dbItoast=self.dbOps.take_photo_from_database(self.username)
#             if not dbIstatus:
#                 return dbIstatus, dbItoast
#             student_verification_result, modelStatus, studentVerifyToast=self.student_verificator.verifyStudent(pil_image1, self.latest_frame)
#             if not modelStatus:
#                 return modelStatus, studentVerifyToast
#             self.per_frame_result["student_verification_toast"] = studentVerifyToast
#             self.result[-1]["student_verification_result"] = student_verification_result
#             verifyStatus=True
#             verifyToast="Student verification completed successfully!"
#             return verifyStatus, verifyToast
#         except Exception as e:
#             # print(f"[ERROR] in verification model! :{e}")
#             verifyToast=f"[ERROR] in verification model! :{e}"
#             verifyStatus=False
#             return verifyStatus, verifyToast
            
            
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from .detection_classes.facePreprocessing import FacePreprocessing
from .detection_classes.objectDetection import ObjectDetectionModule
from .detection_classes.centralisedDatabaseOps import DatabaseOps
from .detection_classes.studentVerification import StudentVerification
import cv2 as cv
import os
import sys
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import time
from concurrent.futures import ThreadPoolExecutor
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

class WebRTCConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=4)  # or more, tune this
        self.loop = asyncio.get_event_loop()
        self.running = True
        self.task_lock = asyncio.Lock()
        self.id_lock = threading.Lock()
        self.object_detector = ObjectDetectionModule()
        self.face_preprocessor = FacePreprocessing()
        self.student_verificator = StudentVerification()
        self.dbOps = DatabaseOps()
        self.latest_frame = None
        self.username = None
        self.last_verification_time = time.time()
        self.per_frame_result={
                                    "fDetection_toast": "",
                                    "facePoints_detection_toast": "",
                                    "gaze_toast": "",
                                    "distance_toast": {
                                        "toast":"",
                                        "distance": 0
                                        },
                                    "object_toast": "",
                                    "student_verification_toast": "",
                                }
        self.result=[]
        self.id=0
        self.final_toast=""

        
    async def connect(self):
        await self.accept()
        self.controller_task = asyncio.create_task(self.controller())
        print("WebSocket connected: Live streaming setup successfully!")
        
    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps({
            "type":"success",
            "final_result": self.result
        }))
        
        await self.object_detector.cleanup()
        await self.face_preprocessor.cleanup()
        await self.student_verificator.cleanup()
        await self.dbOps.cleanup()
        self.per_frame_result=None
        self.result=None
        self.latest_frame = None
        self.username = None
        self.last_verification_time = None
        self.index=None
        self.final_toast=None
        self.running = False
        if self.controller_task:
            self.controller_task.cancel()
            try:
                await self.controller_task
            except asyncio.CancelledError:
                print("Controller task cancelled gracefully.")
        print("WebSocket disconnected: Streaming ended.")
        
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print(type(data))
            print(f"Received signaling message: {data['type']} ")
            print(f"Received username: {data['name']}")
            
            if(data['type']=='frame'):
                base64_str = data['frame'].split(',')[1]
                image_data = base64.b64decode(base64_str)
                img = Image.open(BytesIO(image_data))
                frame=cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
                print(type(frame))
                
                # Ensure dtype is uint8
                if frame.dtype != np.uint8:
                    frame = frame.astype(np.uint8)
                    print("rectangle error")
                self.latest_frame = frame
                self.username = data['name']
            else:
                print(f"Unknown message type received: {data['type']}")
            if data.get("type") == "offer":
                print("Offer received: Live streaming in progress.")
            elif data.get("type") == "new-ice-candidate":
                print("ICE candidate received.")
        except Exception as e:
            print(f"[ERROR] failed to process frame: {e}")
    
    async def controller(self):
        while self.running:
            # ----- Task A: process_frame only -----
            async with self.task_lock:
                if self.latest_frame is not None:
                    print("[TASK A] Running process_frame")
                    process_status, process_toast, per_frame_result, result = await self.loop.run_in_executor(
                        self.executor, self._process_frame_sync
                    )
                    self.per_frame_result = per_frame_result
                    self.result.append(result)
                    if not process_status:
                        self.final_toast = process_toast
                        await self.send(text_data=json.dumps({
                            "type": "fail",
                            "final_toast": self.final_toast,
                        }))
                    else:
                        await self.send(text_data=json.dumps({
                            "type": "success",
                            "final_toast": process_toast,
                            "per_frame_result": self.per_frame_result
                        }))
            await asyncio.sleep(9.9)

            # ----- Task B: process_frame + verification_student -----
            async with self.task_lock:
                if self.latest_frame is not None:
                    print("[TASK B] Running process_frame + verification_student")
                    process_status, process_toast, per_frame_result, result = await self.loop.run_in_executor(
                        self.executor, self._process_frame_sync
                    )
                    if not process_status:
                        self.final_toast = process_toast
                        await self.send(text_data=json.dumps({
                            "type": "fail",
                            "final_toast": self.final_toast,
                        }))
                    self.per_frame_result = per_frame_result
                    self.result.append(result)
                    verify_status, verify_toast, per_frame_result, result = await self.loop.run_in_executor(
                        self.executor, self._verification_student_sync
                    )
                    if not verify_status:
                        self.final_toast = verify_toast
                        await self.send(text_data=json.dumps({
                            "type": "fail",
                            "final_toast": self.final_toast,
                        }))
                    self.per_frame_result["student_verification_toast"] = per_frame_result.get("student_verification_toast", "")
                    self.result[-1]["student_verification_result"]=result
                    if process_status and verify_status:
                        await self.send(text_data=json.dumps({
                            "type": "success",
                            "final_toast": "Both processing and verification succeeded.",
                            "per_frame_result": self.per_frame_result
                        }))
            await asyncio.sleep(0.1)
    
    async def _process_frame_sync(self):
        print("type of frame in process frame fun is : ",type(self.latest_frame))
        with self.id_lock:
            self.id+=1
            current_id = self.id
        per_frame_result=dict()
        result=dict()
        try:
            try:
                faceDetection_status, result_faceDetection, fDetection_toast=self.face_preprocessor.faceDetection(self.latest_frame)
            except Exception as e:
                return False, f"faceDetection() failed: {e}", per_frame_result, result
            try:
                facePoint_status, result_facePoints, facePoints_detection_toast=self.face_preprocessor.faceMesh(self.latest_frame)
            except Exception as e:
                return False, f"faceMesh() failed: {e}", per_frame_result, result
            try:
                frame, gaze_status, gaze_toast, gazeResult=self.face_preprocessor.gaze(self.latest_frame, result_facePoints)
            except Exception as e:
                return False, f"gaze() failed: {e}", per_frame_result, result
            try: 
                frame, minDistance_status, maxDistance_status, inRange_status, distance, minD_toast, min_D_successful_run_status=self.face_preprocessor.minDistance(self.latest_frame, result_faceDetection)
            except Exception as e:
                return False, f"minDistance() failed: {e}", per_frame_result, result
            try:
                frame, object_detection_status, object_detection_result, object_toast=self.object_detector.detect_cheating(self.latest_frame)
            except Exception as e:
                return False, f"objectDetection() failed: {e}"
            if not faceDetection_status or not facePoint_status or not gaze_status or not min_D_successful_run_status or not object_detection_status:
                print("One or more checks failed, returning the frame without further processing.")
                return False, "One or more checks failed, returning the frame without further processing."
            per_frame_result={
                                    "fDetection_toast": fDetection_toast,
                                    "facePoints_detection_toast": facePoints_detection_toast,
                                    "gaze_toast": gaze_toast,
                                    "distance_toast": {
                                        "toast":minD_toast,
                                        "distance": distance
                                        },
                                    "object_toast": object_toast,
                                    "student_verification_toast": "",
                                }
            result={
                                    "id": current_id,
                                    "result_faceDetection": result_faceDetection,
                                    "result_facePoints": result_facePoints,
                                    "gazeResult": gazeResult,
                                    "object_detection_result": object_detection_result,
                                    "student_verification_result": None, 
                                }
                                
            return True,  "Frame processed successfully!", per_frame_result, result
        except Exception as e:
            self.id+=1
            resul={
                    "id": self.id,
                    "error": f"Frame failed due to: {e}"
                }
                
            return False, f"[ERROR] unable to process frames: {e}", per_frame_result, result
        
    async def _verification_student_sync(self):
        per_frame_result = dict()
        result=""
        verifyToast=""
        verifyStatus=False
        try:
            pil_image1, dbIstatus, dbItoast=self.dbOps.take_photo_from_database(self.username)
            if not dbIstatus:
                return dbIstatus, dbItoast
            student_verification_result, modelStatus, studentVerifyToast=self.student_verificator.verifyStudent(pil_image1, self.latest_frame)
            if not modelStatus:
                return modelStatus, studentVerifyToast
            per_frame_result["student_verification_toast"] = studentVerifyToast
            result = student_verification_result
            verifyStatus=True
            verifyToast="Student verification completed successfully!"
            return verifyStatus, verifyToast, per_frame_result, result
        except Exception as e:
            # print(f"[ERROR] in verification model! :{e}")
            verifyToast=f"[ERROR] in verification model! :{e}"
            verifyStatus=False
            return verifyStatus, verifyToast, per_frame_result, result
            