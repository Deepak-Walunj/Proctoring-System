import json
from channels.generic.websocket import AsyncWebsocketConsumer
import pandas as pd
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from .facePreprocessing import FacePreprocessing
from .objectDetection import ObjectDetectionModule
from .centralisedDatabaseOps import DatabaseOps
from .studentVerification import StudentVerification
import cv2 as cv
import os
import sys
import asyncio
import queue
from channels.generic.websocket import AsyncWebsocketConsumer
from google.cloud import speech_v1 as speech
import time
from dotenv import load_dotenv 
from concurrent.futures import ThreadPoolExecutor
# from mlmodel.s3tostt import transcribe_audio,decode_base64_audio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

object_detector = ObjectDetectionModule()
face_preprocessor = FacePreprocessing()
student_verificator = StudentVerification()
dbOps = DatabaseOps()
class WebRTCConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verifyResult = {
            "verified": 0,
            "notVerified": 0,
            "Error": 0
        }
        self.latest_frame = None
        self.latest_username = None
        self.last_verification_time = time.time() 
        
    async def connect(self):
        await self.accept()
        print("WebSocket connected: Live streaming setup successfully!")
        
    async def disconnect(self, close_code):
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
                self.latest_username = data['name']
                cond, face, toast=self.process_frame(frame,face_preprocessor,object_detector)
                print("toast is : ",toast)
                await self.send(text_data=json.dumps({
                    "type":"instruction",
                    "message": toast
                }))
                current_time = time.time()
                if current_time - self.last_verification_time >= 10:
                    self.last_verification_time = current_time
                    verificationResults, verifyStatus, verifyToast = self.verificationStudent(self.latest_frame, student_verificator, dbOps, self.latest_username)
                    await self.send(text_data=json.dumps({
                        "type": "verification",
                        "verificationResults": verificationResults,
                        "verifyToast": verifyToast
                    }))
            else:
                print(f"Unknown message type received: {data['type']}")
            if data.get("type") == "offer":
                print("Offer received: Live streaming in progress.")
            elif data.get("type") == "new-ice-candidate":
                print("ICE candidate received.")
        except Exception as e:
            print(f"[ERROR] failed to process frame: {e}")
    
    def process_frame(self, frame,face_preprocessor,object_detector):
        print("type of frame in process frame fun is : ",type(frame))
        clean_frame=frame.copy()
        try:
            faceDetection_status, result_faceDetection, fDetection_toast=face_preprocessor.faceDetection(frame)
            if not faceDetection_status:
                print(fDetection_toast)
                exit()
            facePoint_status, result_facePoints, facePoints_detection_toast=face_preprocessor.faceMesh(frame)
            if not facePoint_status:
                print(facePoints_detection_toast)
                exit()
            frame, looking_straight_status, gaze_toast, gazeResult=face_preprocessor.gaze(frame, result_facePoints)
            if not looking_straight_status:
                return False ,frame, gaze_toast
            frame, minDistance_status, maxDistance_status, inRange_status, distance, minD_toast=face_preprocessor.minDistance(frame, result_faceDetection)
            if not inRange_status:
                return False ,frame ,minD_toast
            frame, cheating_status, material, object_toast=object_detector.detect_cheating(frame)
            if cheating_status:
                return False,frame,object_toast
        except Exception as e:
            print(f"[ERROR] unable to process frames: {e}")
            
    def verificationStudent(self, frame, student_verificator, dbOps, username):
        verifyToast=""
        verifyStatus=False
        try:
            pil_image1, dbIstatus, dbItoast=dbOps.take_photo_from_database(username)
            if not dbIstatus:
                verifyToast=dbItoast
                verifyStatus=False
                print(f"[ERROR] {dbItoast}")
                return None, verifyStatus, verifyToast
            result, modelStatus, modelVerifyToast=student_verificator.verifyStudent(pil_image1, frame)
            if modelStatus:
                if result.get("verified")==True:
                    print("Student verified!")
                    verifyToast="Student verified!"
                    self.verifyResult["verified"]+=1
                else:
                    print("Anonymous student!")
                    verifyToast="Anonymous student!"
                    self.verifyResult["notVerified"]+=1
            else:
                verifyToast=modelVerifyToast
                verifyStatus=False
                print(f"[ERROR] model error: {verifyToast}")
                self.verifyResult["Error"]+=1
                return None, verifyStatus, verifyToast
            verifyStatus=True
            return self.verifyResult, modelStatus, verifyToast
        except Exception as e:
            print(f"[ERROR] in verification model! :{e}")
            verifyToast=f"[ERROR] in verification model! :{e}"
            verifyStatus=False
            return None, verifyStatus, verifyToast
            