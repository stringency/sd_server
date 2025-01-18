# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from common.log import logger
from common.utils.constants import ResponseCode


class ApiGenericMixin(object):
    def finalize_response(self, request, response, *args, **kwargs):
        """return data format."""
        if not isinstance(response, Response):
            return response
        if response.data is None:
            response.data = {"result": True, "code": ResponseCode.HTTP_200, "message": "success", "data": []}
        elif isinstance(response.data, (list, tuple)):
            response.data = {"result": True, "code": ResponseCode.HTTP_200, "message": "success", "data": response.data}
        elif isinstance(response.data, dict) and not ("result" in response.data):
            if "count" in response.data:
                count = response.data["count"]
                page_size = int(request.query_params.get("size", 10))
                if page_size in [0, -1]:
                    max_page = 1
                elif count % page_size:
                    max_page = int(count / page_size) + 1
                else:
                    max_page = int(count / page_size)
                if "results" in response.data:
                    response.data = {
                        "result": True,
                        "data": response.data["results"],
                        "count": count,
                        "max_page": max_page,
                        "code": ResponseCode.HTTP_200,
                        "message": "success",
                    }
                else:
                    response.data = {
                        "result": True,
                        "data": response.data,
                        "count": count,
                        "code": ResponseCode.HTTP_200,
                        "max_page": max_page,
                        "message": "success",
                    }
            else:
                response.data = {
                    "result": True,
                    "data": response.data,
                    "code": ResponseCode.HTTP_200,
                    "message": "success",
                }

        if response.status_code == status.HTTP_204_NO_CONTENT and request.method == "DELETE":
            response.status_code = status.HTTP_200_OK
        return super(ApiGenericMixin, self).finalize_response(request, response, *args, **kwargs)

#
# class TicketDataPermissionMixin(object):
#     """
#     工单权限控制
#     """
#
#     def get_query_filter(self, role):
#         return role.get_query_filter('工单')
#
#     @staticmethod
#     def is_field_in_q(field_name, q_obj):
#         """
#         判断字段是否在 Q 对象中
#         :param field_name: 要查找的字段名
#         :param q_obj: Q 对象
#         :return: 如果字段在 Q 对象中，返回 True，否则返回 False
#         """
#         if isinstance(q_obj, Q):
#             for child in q_obj.children:
#                 if isinstance(child, Q):
#                     if TicketDataPermissionMixin.is_field_in_q(field_name, child):
#                         return True
#                 elif child[0].startswith(field_name):
#                     return True
#         return False
#
#     def get_queryset(self):
#         queryset = super(TicketDataPermissionMixin, self).get_queryset()
#         user = User.objects.get(username=self.request.user.username)
#         if user.get_is_super():
#             return queryset
#         if not user.role_set.exclude(data_filter='[]').exists():
#             # 没有权限
#             return queryset.none()
#
#         for r in user.role_set.all():
#             cond = self.get_query_filter(r)
#             if self.is_field_in_q('cloud_type', cond):
#                 from service_center.models import LocalWorkOrderService
#                 service_ids = LocalWorkOrderService.objects.filter(
#                     cloud_type_model_id__in=CloudTypeModel.objects.filter(cond).values_list('id', flat=True))
#                 queryset = queryset.filter(local_work_order_service_id__in=service_ids)
#             else:
#                 try:
#                     queryset = queryset.filter(cond)
#                 except Exception:
#                     logger.warning(f'{queryset.model} filter by {cond} failed')
#
#         return queryset
