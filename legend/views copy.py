from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Import models
from object.models import WgtGdObjMst
from layers.models import WgtGdLayerMst, WgtGdPortalLayerMap
from geomStyle.models import WgtGdGeomStyleMst

# Import serializers
from .serializers import LegendRequestSerializer


class LegendAPIView(APIView):
    """
    POST /api/legend/
    payload: {"layer_ids": ["00001","00002"], "options": {"include_bbox": true, "include_sld": true}}
    """
    def post(self, request):
        serializer = LegendRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"statusCode": 400, "statusMessage": "Invalid payload", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        layer_ids = serializer.validated_data['layer_ids']
        options = serializer.validated_data.get('options', {})
        include_bbox = options.get('include_bbox', True)
        include_sld = options.get('include_sld', True)

        layers_qs = WgtGdLayerMst.objects.filter(layer_id__in=layer_ids)
        layer_map = {l.layer_id: l for l in layers_qs}

        obj_ids = [l.obj_id for l in layers_qs if l.obj_id]
        objs = WgtGdObjMst.objects.filter(obj_id__in=obj_ids)
        obj_map = {o.obj_id: o for o in objs}

        styles = WgtGdGeomStyleMst.objects.filter(act_flg='A')
        default_styles = {}
        for s in styles:
            if s.geom_typ not in default_styles:
                default_styles[s.geom_typ] = s

        response_layers = []
        for lid in layer_ids:
            entry = {"layer_id": lid, "errors": []}
            layer = layer_map.get(lid)
            if not layer:
                entry.update({"present": False, "errors": ["layer not found"]})
                response_layers.append(entry)
                continue

            geom_type = layer.layer_geom_typ or (obj_map.get(layer.obj_id).geom_typ if layer.obj_id and obj_map.get(layer.obj_id) else None)
            entry.update({
                "present": True,
                "layer_name": layer.layer_nm,
                "data_source": {
                    "type": layer.layer_data_src_typ,
                    "obj_id": layer.obj_id,
                    "table_name": obj_map.get(layer.obj_id).obj_nm if layer.obj_id and obj_map.get(layer.obj_id) else None,
                    "wms_url": layer.wms_url,
                    "wfs_url": layer.wfs_url,
                    "tile_service": layer.tile_map_service or layer.web_map_tile_service
                },
                "geom_type": geom_type,
                "projection": layer.projection,
                "max_zoom": int(layer.max_zoom) if getattr(layer, 'max_zoom', None) is not None else None,
                "act_flg": layer.act_flg
            })

            style_obj = None
            # portal mapping if exists -> use that style
            portal_map = WgtGdPortalLayerMap.objects.filter(layer_id=lid, act_flg='A').first()
            if portal_map and portal_map.style_id:
                style_obj = WgtGdGeomStyleMst.objects.filter(style_id=portal_map.style_id, act_flg='A').first()
            if not style_obj:
                style_obj = default_styles.get(geom_type)

            if style_obj:
                if include_sld and getattr(style_obj, 'sld_xml_flg', 'N') == 'Y' and style_obj.sld_xml_code:
                    entry["style"] = {
                        "style_id": style_obj.style_id,
                        "sld_xml_flg": style_obj.sld_xml_flg,
                        "legend": {"type": "sld", "payload": {"sld": style_obj.sld_xml_code}}
                    }
                else:
                    entry["style"] = {
                        "style_id": style_obj.style_id,
                        "symbol_type": "point" if geom_type == 'P' else ("line" if geom_type == 'L' else "polygon"),
                        "marker": {
                            "icon_url": getattr(style_obj, 'marker_img_url', None),
                            "fa_name": getattr(style_obj, 'marker_fa_icon_name', None),
                            "color": getattr(style_obj, 'marker_color', None),
                            "size": float(style_obj.marker_size) if getattr(style_obj, 'marker_size', None) is not None else None
                        },
                        "stroke_color": getattr(style_obj, 'stroke_color', None),
                        "fill_color": getattr(style_obj, 'fill_color', None),
                        "stroke_width": float(style_obj.stroke_width) if getattr(style_obj, 'stroke_width', None) is not None else None,
                        "stroke_opacity": float(style_obj.stroke_opacity) if getattr(style_obj, 'stroke_opacity', None) is not None else None,
                        "fill_opacity": float(style_obj.fill_opacity) if getattr(style_obj, 'fill_opacity', None) is not None else None,
                        "legend": {"type": "simple", "payload": {}}
                    }
            else:
                entry["style"] = {"legend": {"type": "simple", "payload": {"note": "no style found"}}}

            if include_bbox:
                if layer.bound_box_from_data == 'Y' and (layer.min_long is not None and layer.min_lat is not None and layer.max_long is not None and layer.max_lat is not None):
                    try:
                        bbox = [float(layer.min_long), float(layer.min_lat), float(layer.max_long), float(layer.max_lat)]
                    except Exception:
                        bbox = None
                else:
                    bbox = None
                entry["bbox"] = bbox

            response_layers.append(entry)

        # Summary metadata for client convenience
        found_ids = [l["layer_id"] for l in response_layers if l.get("present")]
        missing_ids = [lid for lid in layer_ids if lid not in found_ids]
        meta = {
            "requested_count": len(layer_ids),
            "found_count": len(found_ids),
            "missing_count": len(missing_ids),
            "missing_layer_ids": missing_ids
        }

        final_response = {
            "statusCode": 200,
            "statusMessage": "Success",
            "meta": meta,
            "requested_layer_ids": layer_ids,
            "layers": response_layers
        }

        return Response(final_response, status=status.HTTP_200_OK)