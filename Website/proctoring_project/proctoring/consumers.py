import json
from channels.generic.websocket import AsyncWebsocketConsumer
import pandas as pd
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from .facePreprocessing import FacePreprocessing
from .objectDetection import ObjectDetectionModule
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
class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket connected: Live streaming setup successfully!")
        # cv2.namedWindow('imgbox', cv2.WINDOW_NORMAL)

    async def disconnect(self, close_code):
        print("WebSocket disconnected: Streaming ended.")
        cv.destroyAllWindows()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print(type(data))
            print(f"Received signaling message: {data['type']} ")
            # print(f"Received signaling message: {data} ")
            
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
                cond, face, toast=self.process_frame(frame,face_preprocessor,object_detector)
                print("toast is : ",toast)
                await self.send(text_data=json.dumps(toast))
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