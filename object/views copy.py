
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework import status
from django.db import connection
import json




# Import models
from .models import WgtGdObjMst
from layers.models import WgtGdLayerMst

# Import serializers
from .serializers import ObjMstSerializer, LayerObjectRequestSerializer
from layers.serializers import LayerMstSerializer





class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission class that uses our middleware authentication
    """
    def has_permission(self, request, view):
        print(f"IsAuthenticatedCustom: request.custom_user = {request.custom_user}, is_authenticated = {request.custom_user is not None}")
        # Check if we have a custom_user set by our middleware
        return hasattr(request, 'custom_user') and request.custom_user is not None



# Create your views here.

class LayerObjectView(APIView):
    def post(self, request):
        serializer = LayerObjectRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "statusCode": "400",
                "statusMessage": "Invalid request payload",
                "errorInfoList": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        layer_id = serializer.validated_data['layer_id']
        try:
            layer = WgtGdLayerMst.objects.filter(layer_id=layer_id, act_flg='A').first()
            if not layer:
                return Response({
                    "statusCode": "404",
                    "statusMessage": "Layer not found or inactive",
                    "errorInfoList": [f"Layer with ID {layer_id} not found"]
                }, status=status.HTTP_404_NOT_FOUND)

            obj_id = layer.obj_id
            if not obj_id:
                return Response({
                    "statusCode": "404",
                    "statusMessage": "No object associated with this layer",
                    "errorInfoList": [f"No object found for layer {layer_id}"]
                }, status=status.HTTP_404_NOT_FOUND)

            obj = WgtGdObjMst.objects.filter(obj_id=obj_id, act_flg='A').first()
            if not obj:
                return Response({
                    "statusCode": "404",
                    "statusMessage": "Object not found or inactive",
                    "errorInfoList": [f"Object with ID {obj_id} not found"]
                }, status=status.HTTP_404_NOT_FOUND)

            # Fetch GeoJSON from the respective geometry table
            geojson = None
            if obj.obj_nm:
                table_name = obj.obj_nm
                geom_column = 'geom'
                # Compose SQL for GeoJSON FeatureCollection
                sql = f"""
                    SELECT jsonb_build_object(
                        'type', 'FeatureCollection',
                        'features', COALESCE(jsonb_agg(feature), '[]'::jsonb)
                    )
                    FROM (
                        SELECT jsonb_build_object(
                            'type', 'Feature',
                            'geometry', ST_AsGeoJSON({geom_column})::jsonb,
                            'properties', to_jsonb(row) - '{geom_column}'
                        ) AS feature
                        FROM (
                            SELECT * FROM "{table_name}"
                        ) row
                    ) features;
                """
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    geojson = result[0] if result else None
                    if isinstance(geojson, str):
                        geojson = json.loads(geojson)

            return Response({
                "statusCode": "200",
                "statusMessage": "Success",
                "errorInfoList": [],
                "layer": LayerMstSerializer(layer).data,
                "object": ObjMstSerializer(obj).data,
                "geojson": geojson
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": "500",
                "statusMessage": "Internal server error",
                "errorInfoList": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)