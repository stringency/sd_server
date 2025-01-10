from django.db import models


SHORT = 32

class UserInfo(models.Model):
    """用户表"""
    MANAGER = "manager"
    VIP = "vip"
    USER = "user"
    ILLEGAL_USER = "illegal_user"
    ROLE_MAP = (
        (MANAGER, "管理员"),
        (VIP, "VIP用户"),
        (USER, "普通用户"),
        (ILLEGAL_USER, "非法用户"),
    )
    username = models.CharField(verbose_name="用户名", max_length=32, db_index=True)
    password = models.CharField(verbose_name="密码", max_length=64)

    token = models.CharField(verbose_name="TOKEN", max_length=64, null=True, blank=True, db_index=True)

    role = models.CharField(verbose_name="角色", max_length=SHORT, choices=ROLE_MAP, default=USER)
