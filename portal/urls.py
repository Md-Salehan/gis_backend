from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from .views import UserPortalListView 



urlpatterns = [
    path('list/', UserPortalListView.as_view(), name='login'),
    # Add other auth-related endpoints here
]   