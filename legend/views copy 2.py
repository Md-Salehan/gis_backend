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
    Simplified response suitable for basic legends.
    payload: {"layer_ids": ["00001","00002"], "options": {"include_bbox": true, "include_sld": true}}
    """
    def post(self, request):
        serializer = LegendRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"statusCode": 400, "statusMessage": "Invalid payload", "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        layer_ids = serializer.validated_data['layer_ids']
        options = serializer.validated_data.get('options', {})
        include_bbox = options.get('include_bbox', True)
        include_sld = options.get('include_sld', False)  # default: don't return heavy SLD by default

        layers = WgtGdLayerMst.objects.filter(layer_id__in=layer_ids)
        layer_map = {l.layer_id: l for l in layers}

        obj_ids = [l.obj_id for l in layers if l.obj_id]
        objs = WgtGdObjMst.objects.filter(obj_id__in=obj_ids)
        obj_map = {o.obj_id: o for o in objs}

        styles = WgtGdGeomStyleMst.objects.filter(act_flg='A')
        default_styles = {}
        for s in styles:
            if s.geom_typ not in default_styles:
                default_styles[s.geom_typ] = s

        simple_layers = []
        for lid in layer_ids:
            layer = layer_map.get(lid)
            if not layer:
                simple_layers.append({
                    "layer_id": lid,
                    "present": False,
                    "name": None,
                })
                continue

            geom_type = layer.layer_geom_typ or (obj_map.get(layer.obj_id).geom_typ if layer.obj_id and obj_map.get(layer.obj_id) else None)

            # Choose style: portal mapping override -> default by geom type
            style_obj = None
            portal_map = WgtGdPortalLayerMap.objects.filter(layer_id=lid, act_flg='A').first()
            if portal_map and portal_map.style_id:
                style_obj = WgtGdGeomStyleMst.objects.filter(style_id=portal_map.style_id, act_flg='A').first()
            if not style_obj:
                style_obj = default_styles.get(geom_type)

            # Build minimal style payload
            style = {
                "icon": getattr(style_obj, "marker_img_url", None) if style_obj else None,
                "color": getattr(style_obj, "marker_color", None) or getattr(style_obj, "stroke_color", None) if style_obj else None,
                "fill": getattr(style_obj, "fill_color", None) if style_obj else None,
                "width": float(style_obj.stroke_width) if style_obj and getattr(style_obj, "stroke_width", None) is not None else None,
                "sld": style_obj.sld_xml_code if (style_obj and include_sld and getattr(style_obj, "sld_xml_flg", "N") == "Y") else None
            } if style_obj else None

            # Simple bbox
            bbox = None
            if include_bbox and getattr(layer, "bound_box_from_data", None) == 'Y':
                try:
                    if all(getattr(layer, attr) is not None for attr in ("min_long", "min_lat", "max_long", "max_lat")):
                        bbox = [
                            float(layer.min_long),
                            float(layer.min_lat),
                            float(layer.max_long),
                            float(layer.max_lat)
                        ]
                except Exception:
                    bbox = None

            simple_layers.append({
                "layer_id": lid,
                "present": True,
                "name": layer.layer_nm,
                "geom_type": geom_type,
                "style": style,
                "bbox": bbox
            })

        found_count = sum(1 for l in simple_layers if l.get("present"))
        final = {
            "statusCode": 200,
            "statusMessage": "Success",
            "requested_count": len(layer_ids),
            "found_count": found_count,
            "layers": simple_layers
        }
        return Response(final, status=status.HTTP_200_OK)