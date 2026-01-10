from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from object_app.models import WgtGdObjMst
from layers.models import WgtGdLayerMst, WgtGdPortalLayerMap
from geomStyle.models import WgtGdGeomStyleMst

from .serializers import LegendRequestSerializer


class LegendAPIView(APIView):
    """
    POST /api/legend/
    Returns a standardized legend response format.
    payload: {"portal_id": "00001", "layer_ids": ["00001","00002"], "options": {"include_bbox": true, "include_sld": true}}
    """
    def post(self, request):
        serializer = LegendRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        portal_id = serializer.validated_data['portal_id']
        layer_ids = serializer.validated_data['layer_ids']
        
        # First, filter WgtGdPortalLayerMap by portal_id and layer_ids
        portal_layer_maps = WgtGdPortalLayerMap.objects.filter(
            portal_id=portal_id, 
            layer_id__in=layer_ids, 
            act_flg='A'
        )
        
        # Extract layer_ids and style_ids from portal_layer_maps
        portal_map = {plm.layer_id: plm for plm in portal_layer_maps}
        filtered_layer_ids = [plm.layer_id for plm in portal_layer_maps]
        
        # Fetch layers based on filtered layer_ids
        layers = WgtGdLayerMst.objects.filter(layer_id__in=filtered_layer_ids)
        layer_map = {l.layer_id: l for l in layers}

        
        # Extract all style_ids from portal_layer_maps and fetch them
        style_ids = [plm.style_id for plm in portal_layer_maps if plm.style_id]
        custom_styles = WgtGdGeomStyleMst.objects.filter(style_id__in=style_ids, act_flg='A')
        style_map = {s.style_id: s for s in custom_styles}

        legend_layers = []
        for lid in filtered_layer_ids:
            layer = layer_map.get(lid)
            if not layer:
                continue

            # Get style for layer from portal_layer_maps
            portal_map_row = portal_map.get(lid)
            style_obj = None

            if portal_map_row and portal_map_row.style_id:
                style_obj = style_map.get(portal_map_row.style_id)
            

            # Build style dictionary
            style = {
                "fill_color": getattr(style_obj, "fill_color", "#CCCCCC"),
                "stroke_color": getattr(style_obj, "stroke_color", "#000000"),
                "stroke_width": float(getattr(style_obj, "stroke_width", 1) or 1),
                "stroke_opacity": float(getattr(style_obj, "stroke_opacity", 1) or 1),
                "fill_opacity": float(getattr(style_obj, "fill_opacity", 0.7) or 0.7),
                "marker_img_url": getattr(style_obj, "marker_img_url", None),
                "marker_fa_icon_name": getattr(style_obj, "marker_fa_icon_name", None),
                "marker_color": getattr(style_obj, "marker_color", None),
                "marker_size": float(getattr(style_obj, "marker_size", 0) or 0),
                "marker_symbol": getattr(style_obj, "marker_symbol", None),
                "marker_color": getattr(style_obj, "marker_color", None),
            } if style_obj else {}

            # Build layer entry
            layer_entry = {
                "layer_id": lid,
                "layer_nm": layer.layer_nm,
                "type": "categorical",
                "symbols": [{
                    "label": layer.layer_nm,
                    "layer_order_no": portal_map_row.layer_order_no,
                    "geom_type": layer.layer_geom_typ,
                    "style": style,
                }]
            }

            legend_layers.append(layer_entry)

        return Response({
            "success": True,
            "data": legend_layers
        }, status=status.HTTP_200_OK)