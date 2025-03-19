# proctoring/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2 as cv
import numpy as np
from .objectDetection import ObjectDetectionModule  # Import object detection module
import time
class FrameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            """Establish WebSocket connection."""
            self.room_name = "proctoring_room"
            self.room_group_name = f"proctoring_{self.room_name}"
            print("Created room successfully")
            self.object_detector = ObjectDetectionModule()
            print("Object Detection Model Initialized")
            await self.accept()
            print("WebSocket Connection Established")
        except Exception as e:
            print(f"Error in connecting websocket: {e}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        try:
            print("WebSocket Disconnected")
            self.object_detector = None  # Destroy model instance to free resources
        except Exception as e:
            print(f"Error while disconnecting websocket: {e}")
    
    async def receive(self, bytes_data=None):
        try:
            start_time = time.time()  # Measure processing time

            if not bytes_data:
                await self.send(text_data=json.dumps({"status": "error", "message": "No frame received"}))
                return

            print("Receiving frame... Time:", time.time())

            # Convert and process frame
            frame, flag = self.process_frame(bytes_data)
            if not flag:
                await self.send(text_data=json.dumps({"status": "error", "message": "Frame conversion failed"}))
                return

            frame, cheating_detected, object_count, toast = self.object_detector.detect_cheating(frame)

            print(f"Detection complete: {toast} Time:", time.time())

            # If processing time > threshold (e.g., 0.5 sec), log warning
            processing_time = time.time() - start_time
            if processing_time > 0.5:
                print(f"Warning: Slow processing detected ({processing_time:.2f} sec)")

            # Send processed frame
            _, buffer = cv.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            await self.send(bytes_data=frame_bytes)
            await self.send(text_data=json.dumps({"cheating_detected": cheating_detected, "object_count": object_count, "message": toast}))

        except Exception as e:
            print(f"Error processing frame: {e}")
            await self.send(text_data=json.dumps({"status": "error", "message": str(e)}))
            await self.close()


    def process_frame(self, frame_data):
        """Convert raw bytes into an OpenCV image format."""
        print("Processing received frame...")
        try:
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
            if frame is None:
                return None, False
            return frame, True
        except Exception as e:
            return None, False
