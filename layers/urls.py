from django.urls import path, include
from .views import PortalLayersListView



urlpatterns = [
    path('list/', PortalLayersListView.as_view(), name='portal-layers'),
]