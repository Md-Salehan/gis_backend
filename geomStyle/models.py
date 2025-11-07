from django.db import models

# Create your models here.
class WgtGdGeomStyleMst(models.Model):
    style_id = models.CharField(max_length=5, primary_key=True)
    style_nm = models.CharField(max_length=100)
    geom_typ = models.CharField(max_length=1, default='P')
    marker_img_url = models.CharField(max_length=100, blank=True, null=True)
    marker_fa_icon_name = models.CharField(max_length=100, blank=True, null=True)
    marker_color = models.CharField(max_length=7, blank=True, null=True)
    marker_size = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    marker_symbol = models.CharField(max_length=100, blank=True, null=True)
    stroke_color = models.CharField(max_length=7, blank=True, null=True)
    fill_color = models.CharField(max_length=7, blank=True, null=True)
    stroke_width = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    stroke_opacity = models.DecimalField(max_digits=2, decimal_places=2, blank=True, null=True)
    fill_opacity = models.DecimalField(max_digits=2, decimal_places=2, blank=True, null=True)
    label_font_typ = models.CharField(max_length=50, blank=True, null=True)
    label_font_size = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    label_color = models.CharField(max_length=7, blank=True, null=True)
    label_bg_color = models.CharField(max_length=7, blank=True, null=True)
    label_bg_stroke_width = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    label_offset_xy = models.CharField(max_length=20, blank=True, null=True)  # CORRECTED: from label_offset to label_offset_xy
    sld_xml_flg = models.CharField(max_length=1, default='N')
    sld_xml_code = models.CharField(max_length=4000, blank=True, null=True)
    act_flg = models.CharField(max_length=1, default='A')
    mod_dt = models.DateTimeField()

    class Meta:
        db_table = "wgt_gd_geom_style_mst"
        managed = False