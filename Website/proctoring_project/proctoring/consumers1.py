# proctoring/consumers1.py

import os
import sys
import json
import asyncio
import time
import cv2 as cv
import numpy as np
from collections import deque
from channels.generic.websocket import AsyncWebsocketConsumer

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from facePreprocessing import FacePreprocessing

class FaceDetectionConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_queue = deque(maxlen=1)  # Store only the latest frame (drops older frames)
        self.processing = False  # Flag to prevent overlapping processing

    async def connect(self):
        """Establish WebSocket connection."""
        try:
            """Establish WebSocket connection."""
            self.room_name = "proctoring_room1"
            self.room_group_name = f"proctoring_{self.room_name}"
            print("Created room successfully")
            self.face_preprocessor = FacePreprocessing()
            self.connected = True
            print("Object Detection Model Initialized")
            await self.accept()
            print("WebSocket Connection Established")
        except Exception as e:
            print(f"Error in connecting websocket: {e}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        try:
            print("WebSocket Disconnected")
            self.connected = False  # Mark connection as closed
            self.frame_queue.clear()  # Clear pending frames to avoid processing after disconnect
            if self.face_preprocessor:
                del self.face_preprocessor  # Cleanup model instance
        except Exception as e:
            print(f"Error while disconnecting websocket: {e}")

    async def receive(self, bytes_data=None):
        """Receives and queues frames while ensuring minimal lag."""
        try:
            if not bytes_data:
                await self.send(text_data=json.dumps({"status": "error", "message": "No frame received"}))
                return
            self.frame_queue.append(bytes_data)  # Store only the latest frame
            if not self.processing:  # If not already processing, start processing
                self.processing = True
                asyncio.create_task(self.process_latest_frame())
        except Exception as e:
            print(f"Error receiving frame: {e}")
            await self.send(text_data=json.dumps({"status": "error", "message": str(e)}))

    # async def process_latest_frame(self):
    #     """Processes the latest frame in the queue asynchronously."""
    #     while self.frame_queue:
    #         try:
    #             bytes_data = self.frame_queue.popleft()  # Get the latest frame
    #             frame = self.process_frame(bytes_data)
    #             if frame is None:
    #                 await self.send(text_data=json.dumps({"status": "error", "message": "Frame conversion failed"}))
    #                 continue

    #             # Call face detection and face mesh methods
    #             faceDetection_status, result_faceDetection, fDetection_toast = self.face_preprocessor.faceDetection(frame)
    #             facePoint_status, result_facePoints, mDetection_toast = self.face_preprocessor.faceMesh(frame)
                
    #             # Send feedback about the detection status
    #             await self.send(text_data=json.dumps({
    #                 "faceDetection_status": faceDetection_status,
    #                 "facePoint_status": facePoint_status,
    #                 "fDetection_toast": fDetection_toast,
    #                 "mDetection_toast": mDetection_toast
    #             }))

    #             # Send processed frame
    #             _, buffer = cv.imencode('.jpg', frame)
    #             frame_bytes = buffer.tobytes()
    #             await self.send(bytes_data=frame_bytes)
    #         except Exception as e:
    #             print(f"Error processing frame: {e}")
    #             await self.send(text_data=json.dumps({"status": "error", "message": str(e)}))
    #     self.processing = False  # Allow new frames to start processing
        
    async def process_latest_frame(self):
        """Processes the latest frame in the queue asynchronously."""
        while self.frame_queue and self.connected:
            try:
                bytes_data = self.frame_queue.popleft()  # Get the latest frame
                start_time = time.time()
                # Convert and process frame
                frame, flag = self.process_frame(bytes_data)
                if not flag:
                    await self.send(text_data=json.dumps({"status": "error", "message": "Frame conversion failed"}))
                    continue
                faceDetection_status, result_faceDetection, fDetection_toast = self.face_preprocessor.faceDetection(frame)
                facePoint_status, result_facePoints, mDetection_toast = self.face_preprocessor.faceMesh(frame)
                # If processing time > threshold (0.5 sec), log warning
                processing_time = time.time() - start_time
                if processing_time > 0.5:
                    print(f"Warning: Slow processing detected ({processing_time:.2f} sec)")
                # Send processed frame
                if self.connected:  # Ensure connection before sending
                    _, buffer = cv.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    await self.send(bytes_data=frame_bytes)
                    await self.send(text_data=json.dumps({
                    "faceDetection_status": faceDetection_status,
                    "facePoint_status": facePoint_status,
                    "fDetection_toast": fDetection_toast,
                    "mDetection_toast": mDetection_toast
                }))
            except Exception as e:
                print(f"Error processing frame: {e}")
                await self.send(text_data=json.dumps({"status": "error", "message": str(e)}))
        self.processing = False  # Allow new frames to start processing
        
    def process_frame(self, frame_data):
        """Convert raw bytes into an OpenCV image format."""
        try:
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
            return (frame, True) if frame is not None else (None, False)
        except Exception:
            return None, False