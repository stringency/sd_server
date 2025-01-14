from django.db import models

from common.constants.base import (
    DEFAULT_DISPLAY_STRING,
    EMPTY_INT,
    EMPTY_STRING,
    LONG, MIDDLE,
    NORMAL,
    SHORT,
    X_LONG,
    XXX_LONG, XX_LONG
)
from user_management.models import UserInfo


# Create your models here.
class ParamInfo(models.Model):
    """用户表"""
    Param = models.CharField(verbose_name="参数", max_length=NORMAL)


class ImgInfo(models.Model):
    """用户生成图片信息"""
    TXTTOIMG = "txt_to_img"
    IMGTOIMG = "img_to_img"
    IMG_TPYE_MAP = (
        (TXTTOIMG, "文生图"),
        (IMGTOIMG, "图生图"),
    )
    img_path = models.CharField(verbose_name="图片", max_length=XX_LONG)
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=True, blank=True)
    img_type = models.CharField(verbose_name="图片类型", max_length=NORMAL, choices=IMG_TPYE_MAP)
    img_name = models.CharField("图片名称", max_length=X_LONG, default=EMPTY_STRING)
    desc = models.TextField("描述信息", default=EMPTY_STRING)
