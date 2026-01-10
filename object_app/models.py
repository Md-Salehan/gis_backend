from django.db import models

# Create your models here.
class WgtGdObjMst(models.Model):
    obj_id = models.CharField(max_length=5, primary_key=True)
    obj_nm = models.CharField(max_length=50)
    obj_desc = models.CharField(max_length=1000, blank=True, null=True)
    geom_typ = models.CharField(max_length=1, default='N')
    obj_create_typ_flg = models.CharField(max_length=1, default='D')
    act_flg = models.CharField(max_length=1, default='A')
    mod_dt = models.DateTimeField()

    class Meta:
        db_table = "wgt_gd_obj_mst"
        managed = False





