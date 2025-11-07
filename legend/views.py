from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from object.models import WgtGdObjMst
from layers.models import WgtGdLayerMst, WgtGdPortalLayerMap
from geomStyle.models import WgtGdGeomStyleMst

from .serializers import LegendRequestSerializer


class LegendAPIView(APIView):
    """
    POST /api/legend/
    Returns a standardized legend response format.
    payload: {"layer_ids": ["00001","00002"], "options": {"include_bbox": true, "include_sld": true}}
    """
    def post(self, request):
        serializer = LegendRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        layer_ids = serializer.validated_data['layer_ids']
        layers = WgtGdLayerMst.objects.filter(layer_id__in=layer_ids)
        layer_map = {l.layer_id: l for l in layers}

        # Fetch styles and create default style mapping
        styles = WgtGdGeomStyleMst.objects.filter(act_flg='A')
        default_styles = {s.geom_typ: s for s in styles}

        legend_layers = []
        for lid in layer_ids:
            layer = layer_map.get(lid)
            if not layer:
                continue

            # Get style for layer
            portal_map = WgtGdPortalLayerMap.objects.filter(layer_id=lid, act_flg='A').first()
            style_obj = None
            if portal_map and portal_map.style_id:
                style_obj = WgtGdGeomStyleMst.objects.filter(style_id=portal_map.style_id, act_flg='A').first()
            if not style_obj:
                style_obj = default_styles.get(layer.layer_geom_typ)

            # Build style dictionary
            style = {
                "fill_color": getattr(style_obj, "fill_color", "#CCCCCC"),
                "stroke_color": getattr(style_obj, "stroke_color", "#000000"),
                "stroke_width": float(getattr(style_obj, "stroke_width", 1) or 1),  # Default to 1 if None
                "stroke_opacity": float(getattr(style_obj, "stroke_opacity", 1) or 1),  # Default to 1 if None
                "fill_opacity": float(getattr(style_obj, "fill_opacity", 0.7) or 0.7)  # Default to 0.7 if None
            } if style_obj else {}

            # Build layer entry
            layer_entry = {
                "layerId": lid,
                "name": layer.layer_nm,
                "description": layer.obj_nm or "",  # Using obj_nm instead of layer_desc
                "type": "categorical",  # Default to categorical, could be determined by style type
                "visible": True,
                "metadata": {
                    "dateUpdated": layer.mod_dt.strftime("%Y-%m-%d") if getattr(layer, "mod_dt", None) else None,
                },
                "symbols": [{
                    "label": layer.layer_nm,
                    "value": lid,
                    "geom_type": layer.layer_geom_typ,  # Added geom_type from layer
                    "style": style
                }]
            }

            # Remove None values from metadata
            layer_entry["metadata"] = {k: v for k, v in layer_entry["metadata"].items() if v is not None}
            
            legend_layers.append(layer_entry)

        return Response({
            "success": True,
            "data": legend_layers
        }, status=status.HTTP_200_OK)