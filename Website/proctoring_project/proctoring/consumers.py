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
# import asyncio
# import datetime
# from channels.generic.websocket import AsyncWebsocketConsumer
# import time
# from concurrent.futures import ThreadPoolExecutor
# import threading
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

# class VivaConsumers(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.executor = ThreadPoolExecutor(max_workers=10)  # or more, tune this
#         self.loop = asyncio.get_event_loop()
#         self.running = True
#         self.task_lock = asyncio.Lock()
#         self.id_lock = threading.Lock()
#         self.object_detector = ObjectDetectionModule()
#         self.face_preprocessor = FacePreprocessing()
#         self.student_verificator = StudentVerification()
#         self.dbOps = DatabaseOps()
#         self.latest_frame = None
#         self.user_image = None
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
#         self.data=None
        
#     async def connect(self):
#         await self.accept()
#         self.controller_task = asyncio.create_task(self.controller())
#         print("WebSocket connected: Live streaming setup successfully!")
        
#     async def disconnect(self, close_code):
#         await self.send(text_data=json.dumps({
#             "type":"success",
#             "final_result": self.result
#         }))
        
#         self.object_detector=None
#         self.face_preprocessor=None
#         self.student_verificator=None
#         self.dbOps=None
#         self.per_frame_result=None
#         self.result=None
#         self.latest_frame = None
#         self.user_image = None
#         self.last_verification_time = None
#         self.index=None
#         self.final_toast=None
#         self.running = False
#         self.data=None
#         if self.controller_task:
#             self.controller_task.cancel()
#             try:
#                 await self.controller_task
#             except asyncio.CancelledError:
#                 print("Controller task cancelled gracefully.")
#         print("WebSocket disconnected: Streaming ended.")
        
#     async def receive(self, text_data):
#         try:
#             self.data = json.loads(text_data)
#             print(type(self.data))
#             print(f"Received signaling message: {self.data['type']} ")
#             if(self.data['type']=='frame'):
#                 frame_str=self.data['frame']
#                 user_image_str=self.data['user_image']
#                 self.latest_frame=self.convert_image_to_frame_from_string(frame_str)
#                 if self.latest_frame is None:
#                     print("[ERROR] Frame conversion failed. Skipping processing.")
#                     await self.send(text_data=json.dumps({
#                         "type": "fail",
#                         "final_toast": "Frame capture failed. Please check your camera.",
#                     }))
#                 self.user_image=self.convert_image_to_frame_from_string(user_image_str)
#                 print(type(self.user_image))
#                 print(type(self.latest_frame))
#             else:
#                 print(f"Unknown message type received: {self.data['type']}")
#             if self.data.get("type") == "offer":
#                 print("Offer received: Live streaming in progress.")
#             elif self.data.get("type") == "new-ice-candidate":
#                 print("ICE candidate received.")
#         except Exception as e:
#             print(f"[ERROR] failed to process frame: {e}")
    
#     async def controller(self):
#         task_cycle = 0  # 0 for Task A, 1 for Task B
#         while self.running:
#             frame = None
#             user_frame = None
#             # Get current frames
#             if self.latest_frame is not None:
#                 frame = self.latest_frame
#             if self.user_image is not None:
#                 user_frame = self.user_image
                
#             if frame is None:
#                 await asyncio.sleep(1.0)  # Wait if no frame available
#                 continue
                
#             async with self.task_lock:
#                 try:
#                     if task_cycle == 0:
#                         # ----- Task A: Normal detections (every 9 seconds) -----
#                         print("[TASK A] Running process_frame")
                        
#                         try:
#                             process_status, process_toast, per_frame_result, result = await self.loop.run_in_executor(
#                                 self.executor, self._process_frame_sync, frame
#                             )
                            
#                             if not process_status:
#                                 # Update state even on failure
#                                 if per_frame_result:
#                                     self.per_frame_result.update(per_frame_result)
#                                 if result is not None:
#                                     self.result.append(result)
#                                 self.final_toast = process_toast
                                
#                                 await self.send(text_data=json.dumps({
#                                     "type": "fail",
#                                     "final_toast": self.final_toast,
#                                 }))
#                             else:
#                                 # Update state on success
#                                 if per_frame_result:
#                                     self.per_frame_result.update(per_frame_result)
#                                 if result is not None:
#                                     self.result.append(result)
                                    
#                                 await self.send(text_data=json.dumps({
#                                     "type": "success", 
#                                     "final_toast": process_toast,
#                                     "per_frame_result": self.per_frame_result
#                                 }))
                                
#                         except Exception as e:
#                             error_msg = f"[ERROR] Task A(Process Frame) failed in thread: {e}"
#                             print(error_msg)
#                             await self.send(text_data=json.dumps({
#                                 "type": "fail",
#                                 "final_toast": error_msg,
#                             }))
                        
#                         # Switch to Task B for next iteration
#                         task_cycle = 1
#                         sleep_time = 9.0
                        
#                     elif task_cycle == 1:
#                         # ----- Task B: Student verification (every 1 second after Task A) -----
#                         if user_frame is not None:
#                             print("[TASK B] Running verification_student")
                            
#                             try:
#                                 verify_status, verify_toast, per_frame_result, result = await self.loop.run_in_executor(
#                                     self.executor, self._verification_student_sync, frame, user_frame
#                                 )
                                
#                                 if verify_status:
#                                     # Update student verification in existing per_frame_result
#                                     if per_frame_result.get("student_verification_toast"):
#                                         self.per_frame_result["student_verification_toast"] = per_frame_result["student_verification_toast"]
                                    
#                                     # Update the latest result entry with verification data
#                                     if self.result and isinstance(self.result[-1], dict) and result:
#                                         self.result[-1]["student_verification_result"] = result
#                                     elif result:  # If no previous result exists, create new entry
#                                         verification_result = {
#                                             "id": getattr(self, 'id', 0),
#                                             "timestamp": datetime.datetime.now().isoformat(),
#                                             "student_verification_result": result
#                                         }
#                                         self.result.append(verification_result)
                                    
#                                     await self.send(text_data=json.dumps({
#                                         "type": "success",
#                                         "final_toast": "Student verification completed successfully.",
#                                         "per_frame_result": self.per_frame_result
#                                     }))
#                                 else:
#                                     self.final_toast = verify_toast
#                                     await self.send(text_data=json.dumps({
#                                         "type": "fail", 
#                                         "final_toast": verify_toast,
#                                     }))
                                    
#                             except Exception as e:
#                                 error_msg = f"[ERROR] Task B(Student Verification) failed in thread: {e}"
#                                 print(error_msg)
#                                 await self.send(text_data=json.dumps({
#                                     "type": "fail",
#                                     "final_toast": error_msg,
#                                 }))
#                         else:
#                             print("[TASK B] Skipping - no user frame available")
#                             await self.send(text_data=json.dumps({
#                                 "type": "fail",
#                                 "final_toast": "No user image available for verification",
#                             }))
                        
#                         # Switch back to Task A for next iteration  
#                         task_cycle = 0
#                         sleep_time = 1.0
                        
#                 except Exception as e:
#                     error_msg = f"Error in task cycle {task_cycle}: {e}"
#                     print(error_msg)
#                     self.final_toast = error_msg
#                     await self.send(text_data=json.dumps({
#                         "type": "fail",
#                         "final_toast": self.final_toast,
#                     }))
#                     # Continue the cycle even on error
#                     task_cycle = (task_cycle + 1) % 2
#                     sleep_time = 9.0 if task_cycle == 1 else 1.0
            
#             # Sleep based on which task just completed
#             await asyncio.sleep(sleep_time)
    
#     def _process_frame_sync(self, frame):
#         print("type of frame in process frame fun is : ",type(self.latest_frame))
#         with self.id_lock:
#             self.id+=1
#             current_id = self.id
#         per_frame_result=dict()
#         result=dict()
#         try:
#             try:
#                 faceDetection_status, result_faceDetection, fDetection_toast=self.face_preprocessor.faceDetection(self.latest_frame)
#             except Exception as e:
#                 return False, f"faceDetection() failed: {e}", per_frame_result, result
#             try:
#                 facePoint_status, result_facePoints, facePoints_detection_toast=self.face_preprocessor.faceMesh(self.latest_frame)
#             except Exception as e:
#                 return False, f"faceMesh() failed: {e}", per_frame_result, result
#             try:
#                 frame, gaze_status, gaze_toast, gazeResult=self.face_preprocessor.gaze(self.latest_frame, result_facePoints)
#             except Exception as e:
#                 return False, f"gaze() failed: {e}", per_frame_result, result
#             try: 
#                 frame, minDistance_status, maxDistance_status, inRange_status, distance, minD_toast, min_D_successful_run_status=self.face_preprocessor.minDistance(self.latest_frame, result_faceDetection)
#             except Exception as e:
#                 return False, f"minDistance() failed: {e}", per_frame_result, result
#             try:
#                 frame, object_detection_status, object_detection_result, object_toast=self.object_detector.detect_cheating(self.latest_frame)
#             except Exception as e:
#                 return False, f"objectDetection() failed: {e}", per_frame_result, result
#             per_frame_result={
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
#             result={
#                                     "id": current_id,
#                                     "timestamp": datetime.datetime.now().isoformat(),
#                                     "result_faceDetection": result_faceDetection,
#                                     "result_facePoints": result_facePoints,
#                                     "gazeResult": gazeResult,
#                                     "object_detection_result": object_detection_result,
#                                     "student_verification_result": None, 
#                                 }
                                
#             return True,  "Frame processed successfully!", per_frame_result, result
#         except Exception as e:
#             self.id+=1
#             resul={
#                     "id": self.id,
#                     "error": f"Frame failed due to: {e}"
#                 }
                
#             return False, f"[ERROR] unable to process frames: {e}", per_frame_result, result
        
#     def _verification_student_sync(self, frame, user_frame):
#         per_frame_result = dict()
#         result=""
#         verifyToast=""
#         verifyStatus=False
#         try:
#             student_verification_result, modelStatus, studentVerifyToast=self.student_verificator.verifyStudent(frame, user_frame)
#             if not modelStatus:
#                 return modelStatus, studentVerifyToast, per_frame_result, result
#             per_frame_result["student_verification_toast"] = studentVerifyToast
#             result = student_verification_result
#             verifyStatus=True
#             verifyToast="Student verification completed successfully!"
#             return verifyStatus, verifyToast, per_frame_result, result
#         except Exception as e:
#             # print(f"[ERROR] in verification model! :{e}")
#             verifyToast=f"[ERROR] in verification model! :{e}"
#             verifyStatus=False
#             return verifyStatus, verifyToast, per_frame_result, result
            
#     def convert_image_to_frame_from_string(self, image_string):
#         try:
#             if not image_string:
#                 print("[ERROR] Received empty image string.")
#                 return None
#             if ',' in image_string:
#                 base64_str = image_string.split(',')[1]
#             else:
#                 base64_str = image_string
#             print(f"[DEBUG] Base64 string starts with: {base64_str[:30]}...")
#             image_data = base64.b64decode(base64_str)
#             img = Image.open(BytesIO(image_data))
#             frame=cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
#             print(type(frame))
#             # Ensure dtype is uint8
#             if frame.dtype != np.uint8:
#                 frame = frame.astype(np.uint8)
#                 print("rectangle error")
#             print("Image converted successfully")
#             return frame
#         except Exception as e:
#             print(f"Error converting image to frame: {e}")

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
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
import time
from concurrent.futures import ThreadPoolExecutor
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

class VivaConsumers(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.loop = asyncio.get_event_loop()
        self.running = True
        self.task_lock = asyncio.Lock()
        self.id_lock = threading.Lock()
        self.object_detector = ObjectDetectionModule()
        self.face_preprocessor = FacePreprocessing()
        self.student_verificator = StudentVerification()
        self.dbOps = DatabaseOps()
        self.latest_frame = None
        self.user_image = None
        self.last_verification_time = time.time()
        self.per_frame_result = {
            "fDetection_toast": "",
            "facePoints_detection_toast": "",
            "gaze_toast": "",
            "distance_toast": {
                "toast": "",
                "distance": 0
            },
            "object_toast": "",
            "student_verification_toast": "",
        }
        self.result = []
        self.id = 0
        self.final_toast = ""
        self.data = None
        self.controller_task = None
        
    async def connect(self):
        await self.accept()
        self.running = True
        self.controller_task = asyncio.create_task(self.controller())
        print("WebSocket connected: Live streaming setup successfully!")
        
    async def disconnect(self, close_code):
        print(f"WebSocket disconnecting with code: {close_code}")
        
        # Stop the controller first
        self.running = False
        if self.controller_task and not self.controller_task.done():
            self.controller_task.cancel()
            try:
                await self.controller_task
            except asyncio.CancelledError:
                print("Controller task cancelled gracefully.")
        
        # Send final result with proper JSON serialization
        try:
            # Ensure all objects in result are JSON serializable
            serializable_result = self._make_json_serializable(self.result)
            await self.send(text_data=json.dumps({
                "type": "final",
                "final_result": serializable_result
            }))
        except Exception as e:
            print(f"Error sending final result: {e}")
            try:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Session ended with errors"
                }))
            except:
                pass  # WebSocket might already be closed
        
        # Clean up resources
        self._cleanup_resources()
        print("WebSocket disconnected: Streaming ended.")
    
    def _make_json_serializable(self, obj):
        """Convert objects to JSON serializable format"""
        if isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, type):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            return str(obj)
        else:
            return obj
    
    def _cleanup_resources(self):
        """Clean up all resources"""
        self.object_detector = None
        self.face_preprocessor = None
        self.student_verificator = None
        self.dbOps = None
        self.per_frame_result = None
        self.result = None
        self.latest_frame = None
        self.user_image = None
        self.last_verification_time = None
        self.final_toast = None
        self.data = None
        if self.executor:
            self.executor.shutdown(wait=False)
        
    async def receive(self, text_data):
        if not self.running:
            return
            
        try:
            self.data = json.loads(text_data)
            print(f"Received signaling message: {self.data['type']}")
            
            if self.data['type'] == 'frame':
                frame_str = self.data['frame']
                user_image_str = self.data['user_image']
                self.latest_frame = self.convert_image_to_frame_from_string(frame_str)
                if self.latest_frame is None:
                    print("[ERROR] Frame conversion failed. Skipping processing.")
                    await self.send(text_data=json.dumps({
                        "type": "fail",
                        "final_toast": "Frame capture failed. Please check your camera.",
                    }))
                self.user_image = self.convert_image_to_frame_from_string(user_image_str)
                
            elif self.data.get("type") == "offer":
                print("Offer received: Live streaming in progress.")
            elif self.data.get("type") == "new-ice-candidate":
                print("ICE candidate received.")
            else:
                print(f"Unknown message type received: {self.data['type']}")
                
        except Exception as e:
            print(f"[ERROR] failed to process frame: {e}")
    
    async def controller(self):
        """
        Task A: Runs for 9 seconds (9 executions, 1 per second)
        Task B: Runs for 1 second (1 execution)
        Total cycle: 10 seconds
        """
        while self.running:
            try:
                # Task A: Process frame 9 times (once per second for 9 seconds)
                print("[CYCLE] Starting Task A phase (9 seconds, 9 executions)")
                for i in range(9):
                    if not self.running:
                        break
                        
                    frame = self.latest_frame
                    if frame is None:
                        print(f"[TASK A-{i+1}] No frame available, skipping")
                        await asyncio.sleep(1.0)
                        continue
                    
                    print(f"[TASK A-{i+1}/9] Running process_frame")
                    
                    async with self.task_lock:
                        try:
                            process_status, process_toast, per_frame_result, result = await self.loop.run_in_executor(
                                self.executor, self._process_frame_sync, frame
                            )
                            
                            if per_frame_result:
                                self.per_frame_result.update(per_frame_result)
                            if result is not None:
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
                                
                        except Exception as e:
                            error_msg = f"[ERROR] Task A-{i+1} failed in thread: {e}"
                            print(error_msg)
                            await self.send(text_data=json.dumps({
                                "type": "fail",
                                "final_toast": error_msg,
                            }))
                    
                    # Wait 1 second before next execution (unless it's the last iteration)
                    if i < 8 and self.running:
                        await asyncio.sleep(1.0)
                
                if not self.running:
                    break
                
                # Task B: Student verification (1 execution in 1 second)
                print("[CYCLE] Starting Task B phase (1 second, 1 execution)")
                frame = self.latest_frame
                user_frame = self.user_image
                
                if frame is not None and user_frame is not None:
                    print("[TASK B] Running verification_student")
                    
                    async with self.task_lock:
                        try:
                            verify_status, verify_toast, per_frame_result, result = await self.loop.run_in_executor(
                                self.executor, self._verification_student_sync, frame, user_frame
                            )
                            
                            if verify_status:
                                if per_frame_result.get("student_verification_toast"):
                                    self.per_frame_result["student_verification_toast"] = per_frame_result["student_verification_toast"]
                                
                                # Update the latest result entry with verification data
                                if self.result and isinstance(self.result[-1], dict) and result:
                                    self.result[-1]["student_verification_result"] = result
                                elif result:
                                    verification_result = {
                                        "id": getattr(self, 'id', 0),
                                        "timestamp": datetime.datetime.now().isoformat(),
                                        "student_verification_result": result
                                    }
                                    self.result.append(verification_result)
                                
                                await self.send(text_data=json.dumps({
                                    "type": "success",
                                    "final_toast": "Student verification completed successfully.",
                                    "per_frame_result": self.per_frame_result
                                }))
                            else:
                                print("❌ Student not verified.")
                                await self.send(text_data=json.dumps({
                                    "type": "fail", 
                                    "final_toast": verify_toast,
                                }))
                                
                        except Exception as e:
                            error_msg = f"[ERROR] Task B failed in thread: {e}"
                            print(error_msg)
                            await self.send(text_data=json.dumps({
                                "type": "fail",
                                "final_toast": error_msg,
                            }))
                else:
                    print("[TASK B] Skipping - no frame or user frame available")
                    print("❌ Student not verified.")
                    await self.send(text_data=json.dumps({
                        "type": "fail",
                        "final_toast": "No frames available for verification",
                    }))
                
                # Wait 1 second to complete the Task B phase
                if self.running:
                    await asyncio.sleep(1.0)
                    
            except Exception as e:
                if self.running:  # Only log if we're still supposed to be running
                    error_msg = f"Error in controller cycle: {e}"
                    print(error_msg)
                    await self.send(text_data=json.dumps({
                        "type": "fail",
                        "final_toast": error_msg,
                    }))
                    await asyncio.sleep(1.0)  # Prevent tight error loop
        
        print("Controller loop ended")
    
    def _process_frame_sync(self, frame):
        print("type of frame in process frame function is:", type(frame))
        with self.id_lock:
            self.id += 1
            current_id = self.id
            
        per_frame_result = dict()
        result = dict()
        
        try:
            # Face Detection
            try:
                faceDetection_status, result_faceDetection, fDetection_toast = self.face_preprocessor.faceDetection(frame)
            except Exception as e:
                return False, f"faceDetection() failed: {e}", per_frame_result, result
                
            # Face Mesh
            try:
                facePoint_status, result_facePoints, facePoints_detection_toast = self.face_preprocessor.faceMesh(frame)
            except Exception as e:
                return False, f"faceMesh() failed: {e}", per_frame_result, result
                
            # Gaze Detection
            try:
                frame, gaze_status, gaze_toast, gazeResult = self.face_preprocessor.gaze(frame, result_facePoints)
            except Exception as e:
                return False, f"gaze() failed: {e}", per_frame_result, result
                
            # Distance Detection
            try: 
                frame, minDistance_status, maxDistance_status, inRange_status, distance, minD_toast, min_D_successful_run_status = self.face_preprocessor.minDistance(frame, result_faceDetection)
            except Exception as e:
                return False, f"minDistance() failed: {e}", per_frame_result, result
                
            # Object Detection
            try:
                frame, object_detection_status, object_detection_result, object_toast = self.object_detector.detect_cheating(frame)
            except Exception as e:
                return False, f"objectDetection() failed: {e}", per_frame_result, result
            
            per_frame_result = {
                "fDetection_toast": fDetection_toast,
                "facePoints_detection_toast": facePoints_detection_toast,
                "gaze_toast": gaze_toast,
                "distance_toast": {
                    "toast": minD_toast,
                    "distance": distance
                },
                "object_toast": object_toast,
                "student_verification_toast": "",
            }
            
            result = {
                "id": current_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "result_faceDetection": result_faceDetection,
                "result_facePoints": result_facePoints,
                "gazeResult": gazeResult,
                "object_detection_result": object_detection_result,
                "student_verification_result": None, 
            }
            
            return True, "Frame processed successfully!", per_frame_result, result
            
        except Exception as e:
            error_result = {
                "id": current_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": f"Frame failed due to: {e}"
            }
            return False, f"[ERROR] unable to process frames: {e}", per_frame_result, error_result
        
    def _verification_student_sync(self, frame, user_frame):
        per_frame_result = dict()
        result = ""
        verifyToast = ""
        verifyStatus = False
        
        try:
            student_verification_result, modelStatus, studentVerifyToast = self.student_verificator.verifyStudent(frame, user_frame)
            
            if not modelStatus:
                return modelStatus, studentVerifyToast, per_frame_result, result
                
            per_frame_result["student_verification_toast"] = studentVerifyToast
            result = student_verification_result
            verifyStatus = True
            verifyToast = "Student verification completed successfully!"
            
            return verifyStatus, verifyToast, per_frame_result, result
            
        except Exception as e:
            verifyToast = f"[ERROR] in verification model! :{e}"
            verifyStatus = False
            return verifyStatus, verifyToast, per_frame_result, result
            
    def convert_image_to_frame_from_string(self, image_string):
        try:
            if not image_string:
                print("[ERROR] Received empty image string.")
                return None
                
            if ',' in image_string:
                base64_str = image_string.split(',')[1]
            else:
                base64_str = image_string
                
            print(f"[DEBUG] Base64 string starts with: {base64_str[:30]}...")
            image_data = base64.b64decode(base64_str)
            img = Image.open(BytesIO(image_data))
            frame = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
            
            # Ensure dtype is uint8
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
                print("Frame dtype converted to uint8")
                
            print("Image converted successfully")
            return frame
            
        except Exception as e:
            print(f"Error converting image to frame: {e}")
            return None