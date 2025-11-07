# from django.db import models

from django.contrib.gis.db import models



# Create your models here.

class WgtGdLayerMst(models.Model):
    layer_id = models.CharField(max_length=5, primary_key=True)
    layer_nm = models.CharField(max_length=50)
    layer_nature = models.CharField(max_length=1, default='V')
    layer_geom_typ = models.CharField(max_length=1, default='P')
    layer_data_src_typ = models.CharField(max_length=3, default='OBJ')
    obj_id = models.CharField(max_length=5, blank=True, null=True)
    obj_nm = models.CharField(max_length=50, blank=True, null=True)
    file_nm = models.CharField(max_length=100, blank=True, null=True)
    wms_url = models.CharField(max_length=100, blank=True, null=True)
    wfs_url = models.CharField(max_length=100, blank=True, null=True)
    web_map_tile_service = models.CharField(max_length=100, blank=True, null=True)
    tile_map_service = models.CharField(max_length=100, blank=True, null=True)
    survey_layer_flg = models.CharField(max_length=1, default='N')
    app_id = models.CharField(max_length=8, blank=True, null=True)
    form_id = models.CharField(max_length=8, blank=True, null=True)
    layer_edit_flg = models.CharField(max_length=1, default='N')
    bound_box_from_data = models.CharField(max_length=1, default='Y')
    max_lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    max_long = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    min_lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    min_long = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    projection = models.CharField(max_length=20, blank=True, null=True)
    max_zoom = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    act_flg = models.CharField(max_length=1, default='A')
    mod_dt = models.DateTimeField()

    class Meta:
        db_table = "wgt_gd_layer_mst"
        managed = False




class WgtGdPortalLayerMap(models.Model):
    portal_id = models.CharField(max_length=5, primary_key=True)
    layer_id = models.CharField(max_length=5)
    style_id = models.CharField(max_length=5)
    label_text_col_nm = models.CharField(max_length=50, blank=True, null=True)
    label_view_zoom_level = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    override_style_flg = models.CharField(max_length=1, default='N')
    layer_sld_xml_code = models.CharField(max_length=4000, blank=True, null=True)
    act_flg = models.CharField(max_length=1, default='A')
    mod_dt = models.DateTimeField()

    class Meta:
        db_table = "wgt_gd_portal_layer_map"
        unique_together = (("portal_id", "layer_id"),)
        managed = False

    def __str__(self):
        return f"{self.portal_id} - {self.layer_id}"
    






class Feature(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    geometry = models.GeometryField(srid=4326, null=True, blank=True)

    def __str__(self):
        return self.name
