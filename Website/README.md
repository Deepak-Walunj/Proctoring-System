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