from django.db import models


class SutUserMst(models.Model):
    user_id = models.CharField(max_length=25, primary_key=True)
    user_nm = models.CharField(max_length=100)
    user_pwd = models.CharField(max_length=100)
    eff_dt = models.DateField()
    exp_dt = models.DateField(null=True, blank=True)
    login_flg = models.CharField(max_length=1, default="1")
    act_flg = models.CharField(max_length=1, default="A")
    mob_no = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "sut_user_mst"
        managed = False

    @property
    def id(self):
        return self.user_id



class SutLoginAttmptLog(models.Model):
    login_attmpt_no = models.CharField(max_length=20, primary_key=True)
    mod_id = models.CharField(max_length=6, null=True, blank=True)
    user_id = models.CharField(max_length=25)
    pwd = models.CharField(max_length=100)
    ip_addr = models.CharField(max_length=15)
    sucess_flg = models.CharField(max_length=1, default="N")
    fail_rson = models.CharField(max_length=200, null=True, blank=True)
    app_log_no = models.CharField(max_length=20, null=True, blank=True)
    mod_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sut_login_attmpt_log"
        managed = False



class SutAppUserLog(models.Model):
    app_log_no = models.CharField(max_length=20, primary_key=True)
    user_dt = models.DateTimeField()
    ip_addr = models.CharField(max_length=15)
    user_id = models.CharField(max_length=25)
    sys_dt = models.DateField()
    mod_id = models.CharField(max_length=6, default="M0002")
    logout_flg = models.CharField(max_length=1, default="N")
    login_dt = models.DateTimeField()
    logout_dt = models.DateTimeField(null=True, blank=True)
    mob_no = models.CharField(max_length=100, null=True, blank=True)
    login_lvl_ref_cd = models.CharField(max_length=6, default="000002")
    data_lvl_ref_cd = models.CharField(max_length=6, default="000001")
    log_typ = models.CharField(max_length=1, default="A")

    class Meta:
        db_table = "sut_app_user_log"
        managed = False




class SutUserLocMap(models.Model):
    YES_NO_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
    ]

    ACT_FLAG_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('D', 'Deleted'),
    ]

    user_id = models.CharField(max_length=25)
    lvl_ref_cd = models.CharField(max_length=6)

    list_flg = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        default='Y'
    )
    add_flg = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        default='N'
    )
    mod_flg = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        default='N'
    )
    del_flg = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        default='N'
    )
    view_flg = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        default='Y'
    )
    canc_flg = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        default='Y'
    )
    act_flg = models.CharField(
        max_length=1,
        choices=ACT_FLAG_CHOICES,
        default='A'
    )

    mod_dt = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "sut_user_loc_map"
        managed = False
        unique_together = (("user_id", "lvl_ref_cd"),)
        constraints = [
            models.CheckConstraint(
                check=models.Q(list_flg__in=["Y", "N"]),
                name="ck01_sut00069"
            ),
            models.CheckConstraint(
                check=models.Q(add_flg__in=["Y", "N"]),
                name="ck02_sut00069"
            ),
            models.CheckConstraint(
                check=models.Q(mod_flg__in=["Y", "N"]),
                name="ck03_sut00069"
            ),
            models.CheckConstraint(
                check=models.Q(del_flg__in=["Y", "N"]),
                name="ck04_sut00069"
            ),
            models.CheckConstraint(
                check=models.Q(view_flg__in=["Y", "N"]),
                name="ck05_sut00069"
            ),
            models.CheckConstraint(
                check=models.Q(canc_flg__in=["Y", "N"]),
                name="ck06_sut00069"
            ),
            models.CheckConstraint(
                check=models.Q(act_flg__in=["A", "I", "D"]),
                name="ck07_sut00069"
            ),
        ]

    def __str__(self):
        return f"{self.user_id} - {self.lvl_ref_cd}"