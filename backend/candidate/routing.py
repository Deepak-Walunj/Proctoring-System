from django.urls import path
from .consumers import WebRTCConsumer

websocket_urlpatterns = [
    path('ws/', WebRTCConsumer.as_asgi()),
    # path(r"ws/transcribe/", SpeechToTextConsumer.as_asgi()),
]
