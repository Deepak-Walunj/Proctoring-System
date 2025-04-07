from django.urls import re_path
from proctoring.consumers import WebRTCConsumer

websocket_urlpatterns = [
    re_path(r"ws/proctoring/$", WebRTCConsumer.as_asgi()),
]