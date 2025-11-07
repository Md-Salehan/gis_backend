from django.db import models

# Create your models here.
class WgtGdPortalMst(models.Model):
    portal_id = models.CharField(max_length=5, primary_key=True)
    portal_nm = models.CharField(max_length=100)
    portal_desc = models.CharField(max_length=1000, blank=True, null=True)
    portal_url = models.CharField(max_length=100, blank=True, null=True)
    portal_logo_img_url = models.CharField(max_length=100, blank=True, null=True)
    portal_icon = models.CharField(max_length=50, blank=True, null=True)
    bound_box_from_data = models.CharField(max_length=1, default='Y')
    max_lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    max_long = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    min_lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    min_long = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    projection = models.CharField(max_length=20, blank=True, null=True)
    max_zoom = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    map_unit = models.CharField(max_length=20, blank=True, null=True)
    bg_color = models.CharField(max_length=7, blank=True, null=True)
    base_map_typ = models.CharField(max_length=1, default='R')
    base_map_url = models.CharField(max_length=100, blank=True, null=True)
    portal_copyright = models.CharField(max_length=100, blank=True, null=True)
    act_flg = models.CharField(max_length=1, default='A')
    mod_dt = models.DateTimeField()

    class Meta:
        db_table = "wgt_gd_portal_mst"
        managed = False



class WgtGdPortalUserMap(models.Model):
    portal_id = models.CharField(max_length=5)
    user_id = models.CharField(max_length=25)
    privilege_flg = models.CharField(max_length=1, default='V')
    act_flg = models.CharField(max_length=1, default='A')
    mod_dt = models.DateTimeField()

    class Meta:
        db_table = "wgt_gd_portal_user_map"
        managed = False
        unique_together = (("portal_id", "user_id"),)