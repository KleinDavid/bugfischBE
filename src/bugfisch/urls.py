from django.urls import path
from bugfisch import views
from objects.websocket.consumer import Consumer

urlpatterns = [
    path('executeAction/', views.ExecuteAction.as_view(), name='Action')
]

websocket_urlpatterns = [
    path('actions', Consumer),
]
