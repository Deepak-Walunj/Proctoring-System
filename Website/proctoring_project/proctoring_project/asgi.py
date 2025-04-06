# proctoring_project/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from proctoring import consumers  # Import your consumers
from proctoring import consumers1

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proctoring_project.settings')

# WebSocket URL routing
websocket_urlpatterns = [
    path("ws/object-detection/", consumers.ObjectDetectionConsumer.as_asgi()),  # Ensure you're using FrameConsumer
    path("ws/face-detection/", consumers1.FaceDetectionConsumer.as_asgi())
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handle HTTP requests
    "websocket": URLRouter(websocket_urlpatterns),  # Handle WebSocket connections
})
