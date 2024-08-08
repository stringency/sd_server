from django.db import models

# Create your models here.
class ParamInfo(models.Model):
    """用户表"""
    Param = models.CharField(verbose_name="参数", max_length=32)
