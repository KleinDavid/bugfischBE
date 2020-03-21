from bugfisch import urls
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.urls import path
from objects.websocket.consumer import Consumer
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [path('actions', Consumer)],
            )
        )
    ),
})