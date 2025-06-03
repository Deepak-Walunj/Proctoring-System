# proctoring_project/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import proctoring.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proctoring_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            proctoring.routing.websocket_urlpatterns
            )
    ),
})