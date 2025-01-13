from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from user_management import models


# URL token身份认证
class QueryParamsAuthentication(BaseAuthentication):
    # 做用户的认证
    # 1.读取请求传递的token
    # 2.校验合法性
    # 3.返回值1.元组.2.错误信息.3.多个认证类--匿名用户
    def authenticate(self, request):
        # 获取token
        token = request.query_params.get("token")
        # print("QueryParamsAuthentication",token)
        if not token:
            return
        # 校验token
        user_object = models.UserInfo.objects.filter(token=token).first()
        print(user_object)
        # print("QueryParamsAuthentication", user_object)
        if user_object:
            return user_object, token  # 返回的元组将会赋值到request的属性当中
        return

    def authenticate_header(self, request):
        return "URLAUTH"


# 请求头token认证
# Authorization = a322923b-5fc3-4f1d-b76c-8dbc6b901176
class HeaderAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 获取token
        token = request.META.get("HTTP_AUTHORIZATION")
        # print(username)
        # print("HeaderAuthentication", token)
        if not token:
            return
        # 校验token
        user_object = models.UserInfo.objects.filter(token=token).first()
        # print("HeaderAuthentication", user_object)
        if user_object:
            return user_object, token  # 返回的元组将会赋值到request的属性当中
        return

    def authenticate_header(self, request):
        return "HEADERAUTH"


# 拒绝匿名的认证
class NOAuthentication(BaseAuthentication):
    def authenticate(self, request):
        raise AuthenticationFailed({"msg": "认证失败！"})

    def authenticate_header(self, request):
        return "AUTHORIZATION_ERROR"

