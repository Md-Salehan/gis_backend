from django.urls import path
from .views import LegendAPIView

urlpatterns = [
    path('', LegendAPIView.as_view(), name='legend'),
]