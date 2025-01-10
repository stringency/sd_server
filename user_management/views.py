import uuid

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user_management import models
from user_management.serializers import UserInfoSerializer


class UserInfoView(ModelViewSet):
    """用户信息操作"""
    # permission_classes = [VipPermission, ManagerPermission]  # 管理员和会员
    # throttle_classes = [VipThrottle]

    # 条件筛选
    # filter_backends = [DjangoFilterBackend,]
    # filterset_class = UserInfoFilterSet

    queryset = models.UserInfo.objects.all()
    serializer_class = UserInfoSerializer

    @action(methods=["post"], detail=False, url_path="register")
    def register(self, request, *args, **kwargs):
        """用户注册"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "注册成功"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"], detail=False, url_path="login")
    def login(self, request, *args, **kwargs):
        """用户登录"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            # 为用户生成一个唯一的Token
            user.token = uuid.uuid4().hex
            user.save()
            return Response({
                "message": "登录成功",
                "token": user.token,
                "username": user.username,
                "role": user.get_role_display(),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)