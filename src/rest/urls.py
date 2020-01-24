from django.urls import path
from . import views


urlpatterns = [
    path('executeAction/', views.ExecuteAction.as_view(), name='Action')
]