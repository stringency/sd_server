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
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    IMG_STATUS_MAP = (
        (PENDING, "正在生图"),
        (SUCCESS, "生图完成"),
        (FAILURE, "生图失败"),
    )

    img_path = models.CharField(verbose_name="图片地址", max_length=XX_LONG, null=True)
    img_logo = models.BinaryField(verbose_name="图片缩略图", max_length=XX_LONG, null=True)
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=True, blank=True)
    img_type = models.CharField(verbose_name="图片类型", max_length=NORMAL, choices=IMG_TPYE_MAP, default=TXTTOIMG)
    img_name = models.CharField("图片名称", max_length=X_LONG, null=True)
    img_status = models.CharField("图片状态", max_length=X_LONG, choices=IMG_STATUS_MAP, default=PENDING)
    task_id = models.TextField("任务ID", null=True)
    desc = models.TextField("描述信息", null=True)

