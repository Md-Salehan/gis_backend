

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission



# Import models
from .models import WgtGdPortalMst, WgtGdPortalUserMap
# Import serializers
from .serializers import PortalSerializer



class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission class that uses our middleware authentication
    """
    def has_permission(self, request, view):
        print(f"IsAuthenticatedCustom: request.custom_user = {request.custom_user}, is_authenticated = {request.custom_user is not None}")
        # Check if we have a custom_user set by our middleware
        return hasattr(request, 'custom_user') and request.custom_user is not None



class UserPortalListView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        # Get user from custom_user (JWT)
        user_id = request.custom_user.user_id
        
        portal_ids = WgtGdPortalUserMap.objects.filter(
            user_id=user_id, act_flg='A'
        ).values_list('portal_id', flat=True)
        portals = WgtGdPortalMst.objects.filter(
            portal_id__in=portal_ids, act_flg='A'
        )
        serializer = PortalSerializer(portals, many=True)
        return Response(serializer.data)