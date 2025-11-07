from django.urls import path, include
from .views import LayerObjectView

urlpatterns = [
    path('layer-object/', LayerObjectView.as_view(), name='layer-object'),
]