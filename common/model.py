# -*- coding: utf-8 -*-
import copy

from django.db import models
from django.db.models import fields
from django.db.models.query import QuerySet

from common.constants.base import EMPTY_INT, EMPTY_STRING, NORMAL, LONG

DEFAULT_ADD_LOG = True  # 是否默认添加日志


def params_conver(m, data):
    try:
        if not m:
            return {}
        if type(m) == fields.DateTimeField:
            return data.strftime("%Y-%m-%d %H:%M:%S")
        if type(m) == fields.related.ForeignKey:
            return data.to_dict()
        return data
    except Exception:
        return {}


class ResourceBaseModel(models.Model):
    """Resource Base Model"""
    resource_id = models.CharField("资源ID", max_length=LONG, default=EMPTY_STRING, db_index=True)
    resource_name = models.CharField("资源名称", max_length=LONG, default=EMPTY_STRING, db_index=True)

    class Meta:
        abstract = True
        ordering = ["-id"]

    def to_dict(self):
        return {f.name: params_conver(f, getattr(self, f.name)) for f in self._meta.fields}
