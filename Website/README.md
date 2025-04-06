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

using Redis + websocket
Redis (Port 6379) → Acts as a message broker to manage WebSocket connections across multiple Django processes.
Django WebSockets (Port 8000) → Handles incoming WebSocket connections via Django Channels.

🔍 How It Works?
A WebSocket client connects to ws://localhost:8000/ws/some_endpoint/.
Django Channels accepts the WebSocket connection and routes it to the correct consumer.
The channels_redis backend stores WebSocket connection data in Redis.
If multiple WebSocket connections occur:
Django Channels (on port 8000) still processes them.
Redis (on port 6379) helps manage these connections efficiently across multiple workers.

🌟 Why Is Redis Needed?
The default InMemoryChannelLayer cannot handle multiple WebSocket connections in different processes.
If you deploy with multiple workers (Gunicorn, Daphne, ASGI workers, etc.), each worker needs to share WebSocket data, which Redis enables.
Redis acts as a message bus so that WebSocket events can be shared across multiple instances of your Django app.

🚀 How to Confirm It’s Working?
Run Redis (redis-server should be active on 6379).
Start Django ASGI server (daphne -b 0.0.0.0 -p 8000 proctoring_project.asgi:application).
Open two browser tabs or use wscat to connect two WebSockets to ws://localhost:8000/ws/some_endpoint/.
If both connect successfully and receive messages without interference, it means multiple connections are working correctly.

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