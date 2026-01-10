from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework import status
from django.db import connection
import json




# Import models
from .models import WgtGdObjMst
from layers.models import WgtGdLayerMst, WgtGdPortalLayerMap
from geomStyle.models import WgtGdGeomStyleMst

# Import serializers
from .serializers import ObjMstSerializer, LayerObjectRequestSerializer
from layers.serializers import LayerMstSerializer, PortalLayerMapSerializer





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
        portal_id = serializer.validated_data['portal_id']
        
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

            # Get style_id from portal layer map
            portal_layer_map = WgtGdPortalLayerMap.objects.filter(
                portal_id=portal_id,
                layer_id=layer_id, 
                act_flg='A'
            ).first() 

            if not portal_layer_map:
                return Response({
                    "statusCode": "404",
                    "statusMessage": "Portal layer mapping not found or inactive",
                    "errorInfoList": [f"No mapping found for portal {portal_id} and layer {layer_id}"]
                }, status=status.HTTP_404_NOT_FOUND)
                       
            style_id = portal_layer_map.style_id if portal_layer_map else None
            style_props = None
            # In the LayerObjectView class, update the style_props section:
            if style_id:
                style = WgtGdGeomStyleMst.objects.filter(style_id=style_id, act_flg='A').first()
                if style:
                    # Convert Decimal fields to float for JSON serialization
                    style_props = {
                        "style_id": style.style_id,
                        "style_nm": style.style_nm,
                        "geom_typ": style.geom_typ,
                        "marker_img_url": style.marker_img_url,
                        "marker_fa_icon_name": style.marker_fa_icon_name,
                        "marker_color": style.marker_color,
                        "marker_size": int(style.marker_size) if style.marker_size is not None else None,
                        "marker_symbol": style.marker_symbol,
                        "stroke_color": style.stroke_color,
                        "fill_color": style.fill_color,
                        "stroke_width": int(style.stroke_width) if style.stroke_width is not None else None,
                        "stroke_opacity": float(style.stroke_opacity) if style.stroke_opacity is not None else None,
                        "fill_opacity": float(style.fill_opacity) if style.fill_opacity is not None else None,
                        "label_font_typ": style.label_font_typ,
                        "label_font_size": int(style.label_font_size) if style.label_font_size is not None else None,
                        "label_color": style.label_color,
                        "label_bg_color": style.label_bg_color,
                        "label_bg_stroke_width": int(style.label_bg_stroke_width) if style.label_bg_stroke_width is not None else None,
                        "label_offset_xy": style.label_offset_xy,
                        "sld_xml_flg": style.sld_xml_flg,
                        "sld_xml_code": style.sld_xml_code,
                    }
            # Fetch GeoJSON from the respective geometry table
            geojson = None
            if obj.obj_nm:
                table_name = obj.obj_nm
                geom_column = 'geom'
                # Compose SQL for GeoJSON FeatureCollection without injecting style properties into feature properties
                sql = f"""
                    SELECT jsonb_build_object(
                        'type', 'FeatureCollection',
                        'features', COALESCE(jsonb_agg(feature), '[]'::jsonb)
                    )
                    FROM (
                        SELECT jsonb_build_object(
                            'type', 'Feature',
                            'geometry', ST_AsGeoJSON(ST_Transform({geom_column}, 4326))::jsonb,
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
                "metaData": {
                    "layer": LayerMstSerializer(layer).data,
                    "object": ObjMstSerializer(obj).data,
                    "style": style_props,
                    "portal_layer_map": PortalLayerMapSerializer(portal_layer_map).data,
                },
                "geojson": geojson,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": "500",
                "statusMessage": "Internal server error",
                "errorInfoList": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)