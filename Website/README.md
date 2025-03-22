frontend overview:
The camera captures frames every 300ms.
The WebSocket connects to ws://localhost:8000/ws/proctoring/.
When proctoring starts, the webcam stream is acquired, and frames are sent via WebSocket.
The frames are converted to grayscale and sent in JPEG format with 0.5 quality to reduce bandwidth usage.
The WebSocket receives either:
JSON data (detection results such as cheating detection, object count).
Blob data (processed video frame), which is displayed on the frontend.
If the WebSocket closes, it attempts to reconnect up to 5 times with a random delay (0-5s).
Pressing Enter stops the proctoring.

Backend Overview:
WebSocket Consumer:
The backend uses Django Channels to manage WebSocket connections. The main consumer is FrameConsumer, which handles real-time frame processing.
Connection Handling:
The WebSocket is established when the frontend connects to ws://localhost:8000/ws/proctoring/.
A room named "proctoring_room" is created for managing the session.
The ObjectDetectionModule is initialized when a connection is established.
Frame Reception & Queueing:
The backend receives frames from the frontend via WebSocket messages.
Frames are stored in a deque with maxlen=1, ensuring only the latest frame is processed (minimizing lag).
If no frames are received, an error response is sent to the frontend.
Frame Processing Pipeline:
The latest frame is dequeued.
The frame is converted from raw bytes to an OpenCV image format.
The ObjectDetectionModule is used to analyze the frame for cheating behavior.
The processed frame, along with cheating detection results (boolean flag, object count, message), is sent back to the frontend.
Performance Considerations:
Frame Processing Rate: If processing takes longer than 0.5 seconds, a warning is logged.
Asynchronous Processing: The asyncio.create_task() function is used to prevent blocking and ensure new frames are handled efficiently.
Disconnection Handling:
When the WebSocket disconnects, resources such as the object detection model are released.
Error handling ensures smooth cleanup if an issue occurs.

Comparison With Object Detection:

Scenario	                        Detection Time	    Next Frame Interval
Object Detected	                        48.6ms	            100.2ms
Nothing Detected (First Frame)	        155ms	            7.2ms
Nothing Detected (Second Frame)	        ~7.2ms	            ~7.2ms

if cellphone is there for 6 seconds in the frame then it makrs as cheating


Scaling for 1 Million Users
Your backend needs horizontal scaling using:
Load Balancing: Deploy behind NGINX or AWS ALB.
WebSocket Scaling:
Use Django Channels with Redis for distributed WebSocket handling.
Offload processing to Celery workers.
Streaming Alternative:
Instead of WebSockets, use WebRTC (reduces server load).
GPU Utilization:
Optimize Object Detection with TensorRT or OpenVINO (reduces CPU usage).
Use a Dedicated CDN for image delivery instead of WebSocket transmission.