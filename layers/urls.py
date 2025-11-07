from django.urls import path, include
from .views import PortalLayersListView

from rest_framework.routers import DefaultRouter
from layers.views import FeatureViewSet

router = DefaultRouter()
router.register(r'features', FeatureViewSet)

urlpatterns = [
    path('list/', PortalLayersListView.as_view(), name='portal-layers'),
    path('crud/', include(router.urls)),
]