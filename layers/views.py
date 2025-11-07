from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework import status

from rest_framework import viewsets

# Import models
from .models import WgtGdLayerMst, WgtGdPortalLayerMap, Feature
from portal.models import WgtGdPortalMst
from geomStyle.models import WgtGdGeomStyleMst

# Import serializers
from .serializers import LayerMstSerializer, PortalLayersRequestSerializer, PortalLayerMapSerializer, FeatureSerializer
from portal.serializers import PortalSerializer
from geomStyle.serializers import GeomStyleMstSerializer

class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission class that uses our middleware authentication
    """
    def has_permission(self, request, view):
        print(f"IsAuthenticatedCustom: request.custom_user = {request.custom_user}, is_authenticated = {request.custom_user is not None}")
        # Check if we have a custom_user set by our middleware
        return hasattr(request, 'custom_user') and request.custom_user is not None

class PortalLayersListView(APIView):
    permission_classes = [IsAuthenticatedCustom]
    
    def post(self, request):
        serializer = PortalLayersRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "statusCode": "400",
                "statusMessage": "Invalid request payload",
                "errorInfoList": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        portal_id = serializer.validated_data['portal_id']
        
        try:
            # FIX: Use get() instead of filter().exists() to get the actual portal instance
            portal_mst = WgtGdPortalMst.objects.get(
                portal_id=portal_id, 
                act_flg='A'
            )
            
            portal_mst_data = PortalSerializer(portal_mst).data
            
            portal_layers = WgtGdPortalLayerMap.objects.filter(
                portal_id=portal_id,
                act_flg='A'
            ).order_by('layer_id')
            
            if not portal_layers.exists():
                return Response({
                    "statusCode": "404", 
                    "statusMessage": "No layers found for this portal",
                    "errorInfoList": [f"No active layers found for portal {portal_id}"],
                    "layers": []
                }, status=status.HTTP_404_NOT_FOUND)
            
            layers_data = []
            for layer_map in portal_layers:
                layer_map_data = PortalLayerMapSerializer(layer_map).data
                try:
                    layer_mst = WgtGdLayerMst.objects.get(layer_id=layer_map.layer_id, act_flg='A')
                    layer_mst_data = LayerMstSerializer(layer_mst).data
                    geomStyle_mst = WgtGdGeomStyleMst.objects.get(style_id=layer_map.style_id, act_flg='A')
                    geomStyle_mst_data = GeomStyleMstSerializer(geomStyle_mst).data
                except WgtGdLayerMst.DoesNotExist:
                    layer_mst_data = None
                    geomStyle_mst_data = None
                layer_map_data['layer_mst'] = layer_mst_data
                layer_map_data['geomStyle_mst'] = geomStyle_mst_data
                layers_data.append(layer_map_data)
            
            return Response({
                "statusCode": "200",
                "statusMessage": "Success",
                "errorInfoList": [],
                "portalId": portal_id,
                "totalLayers": portal_layers.count(),
                "layers": layers_data,
                "portalDetails": portal_mst_data
            }, status=status.HTTP_200_OK)
            
        except WgtGdPortalMst.DoesNotExist:
            return Response({
                "statusCode": "404",
                "statusMessage": "Portal not found or inactive",
                "errorInfoList": [f"Portal with ID {portal_id} not found"]
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error fetching portal layers: {str(e)}")
            return Response({
                "statusCode": "500",
                "statusMessage": "Internal server error",
                "errorInfoList": ["An unexpected error occurred"]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        








class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer