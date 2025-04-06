import json
from channels.generic.websocket import AsyncWebsocketConsumer
import pandas as pd
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from .FacePreprocessing import FacePreprocessing
from .objectDetection import ObjectDetectionModule
import cv2 as cv
import os
import sys
import asyncio
import queue

from channels.generic.websocket import AsyncWebsocketConsumer


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

object_detector = ObjectDetectionModule()
face_preprocessor = FacePreprocessing()

def decode_base64(data):
    # Extract the base64 string without the prefix (e.g., 'data:image/jpeg;base64,')
    base64_str = data.split(",")[1]
    img_data = base64.b64decode(base64_str)
    img = Image.open(BytesIO(img_data))
    return img  

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
                # Decode the base64 string
                image_data = base64.b64decode(base64_str)
                # Create an image from the decoded bytes
                img = Image.open(BytesIO(image_data))
                # open_cv_image = np.array(img)
                # frame = open_cv_image[:, :, ::-1].copy()
                frame=cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
                print(type(frame))
    # Ensure dtype is uint8
                if frame.dtype != np.uint8:
                    frame = frame.astype(np.uint8)
                    print("rectangle error")
                    print(frame,face_preprocessor,object_detector)
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
            facePoint_status, result_facePoints, mDetection_toast=face_preprocessor.faceMesh(frame)
            if not facePoint_status:
                print(mDetection_toast)
                exit()
            frame, looking_straight_status, gaze_toast=face_preprocessor.gaze(frame, result_facePoints)
            if not looking_straight_status:
                return False ,frame,gaze_toast
            frame, minDistance_status, maxDistance_status, inRange_status, distance, minD_toast=face_preprocessor.minDistance(frame, result_faceDetection)
            if not inRange_status:
                return False ,frame,minD_toast
            frame, singleFace_status, box_faces, non_box_faces, singleF_toast= face_preprocessor.singleFaceInsideBox(frame, result_faceDetection)
            if not singleFace_status:
                return False,frame, singleF_toast
            frame, cheating_status, material, object_toast=object_detector.detect_cheating(frame)
            if cheating_status:
                return False,frame,object_toast
            # cv.imshow("Camera", frame)
            font_scale = 0.5  
            thickness = 2
            height, width, _ = frame.shape
            bottom_right_x, bottom_right_y = int(width * 0.0), int(height * 0.9)
            # cv.imshow("Camera", frame)
            key = cv.waitKey(1)
            if key == 27:  # ESC
                print("Exiting...")
                cv.destroyAllWindows()
                return False, None, "Program exited"
            elif key == 13 :
                # capture_image=False
                if singleFace_status and box_faces==1 and not cheating_status and inRange_status and looking_straight_status:
                    # cv.putText(frame, "Face Captured", 
                        # (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
                    # cv.imshow("Camera", frame)
                    cv.waitKey(1000)
                    print("Size of the taken image:", clean_frame.shape)
                    cropFace_status, cropped_face, cropF_toast=face_preprocessor.crop_face(clean_frame, result_faceDetection)
                    if cropFace_status==False:
                        print(cropF_toast)

                        cv.destroyAllWindows()
                        return False, None, cropF_toast
                    else:
                        print(cropF_toast)
                    
                    detectLandmarks_status, tobe_align_face, count_final_landmarks, left_eye_landmark, right_eye_landmark, landmark_toast=face_preprocessor.detect_landmarks(cropped_face, result_facePoints)
                    if detectLandmarks_status==False:
                        print(landmark_toast)

                        cv.destroyAllWindows()
                        return False, None, landmark_toast
                    elif left_eye_landmark is  None or right_eye_landmark is None:
                        landmark_toast="Not able to find the eyes landmarks! Something is obstructing!"
                        print(landmark_toast)

                        cv.destroyAllWindows()
                        return False, None, landmark_toast
                    elif count_final_landmarks <468:
                        landmark_toast="Not enough landmarks detected! Please try again"
                        print(landmark_toast)

                        cv.destroyAllWindows()
                        return False, None, landmark_toast
                    else:
                        print(landmark_toast)
                    alignFace_status, final_align_face, fAlign_toast=face_preprocessor.align_face(tobe_align_face, left_eye_landmark, right_eye_landmark)
                    if alignFace_status==False:
                        print(fAlign_toast)

                        cv.destroyAllWindows()
                        return False, None, fAlign_toast
                    else:
                        print(fAlign_toast)

                        cv.destroyAllWindows()
                        return True, final_align_face, fAlign_toast
                # elif not looking_straight_status:
                #     cv.putText(frame, gaze_toast, 
                #         (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                #     cv.imshow("Camera", frame)
                #     cv.waitKey(1000)
                # elif not singleFace_status and box_faces>1 and non_box_faces>1 and not cheating_status:
                #     cv.putText(frame, "multiple faces detected", 
                #         (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                #     cv.imshow("Camera", frame)
                #     cv.waitKey(1000)
                # elif not singleFace_status and box_faces<1 and not cheating_status:
                #     cv.putText(frame, "No face detected", 
                #         (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                #     cv.imshow("Camera", frame)
                #     cv.waitKey(1000)
                # elif cheating_status and singleFace_status and box_faces==1 and inRange_status:
                #     cv.putText(frame, f"{material} detected! try again", 
                #         (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                #     cv.imshow("Camera", frame)
                #     cv.waitKey(1000)
                # elif singleFace_status and not inRange_status and not cheating_status:
                #     cv.putText(frame, f"Distance: {int(distance)} cm", 
                #         (bottom_right_x, bottom_right_y + int(height * 0.03)), cv.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                #     cv.imshow("Camera", frame)
                #     cv.waitKey(1000)
        except Exception as e:
            print(f"[ERROR] unable to process frames: {e}")
            cv.destroyAllWindows()

            # Wait for a key press (this can be used for timing control or closing)
            # cv.waitKey(1)
            # response = {
            #     "type": "ack",
            #     "message": f"Message of type '{data['type']}' received successfully!"
            # }
            # if cheating["type"]:

                # await self.send(text_data=json.dumps(cheating["warn"]))
                

        # await self.send(text_data=json.dumps(data))

        # Example: Check for specific events (like ICE candidate or SDP)
        