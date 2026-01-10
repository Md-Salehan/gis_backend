from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomLoginView, LogoutView



urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # Add other auth-related endpoints here
]   