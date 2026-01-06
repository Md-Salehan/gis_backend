from django.urls import path
from .views import PrintMapView

urlpatterns = [
    path("map/", PrintMapView.as_view(), name="print-map"),
]
