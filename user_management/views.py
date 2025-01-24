import uuid

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from SDTasks.models import ImgInfo
from user_management.models import UserInfo
from user_management.serializers import UserInfoSerializer, RegisterSerializer, LoginSerializer, UserImgInfoSerializer

from common.utils.custom_response import Success, Fail


class UserInfoView(ModelViewSet):
    """用户信息操作"""
    # permission_classes = [VipPermission, ManagerPermission]  # 管理员和会员
    # throttle_classes = [VipThrottle]

    # 条件筛选
    # filter_backends = [DjangoFilterBackend,]
    # filterset_class = UserInfoFilterSet

    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer

    @action(methods=["post"], detail=False, authentication_classes=[])
    def register(self, request, *args, **kwargs):
        """用户注册"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("confirm_password")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Success(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=["post"], detail=False, authentication_classes=[])
    def login(self, request, *args, **kwargs):
        """用户登录"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserInfo.objects.filter(**serializer.validated_data).first()
        if not user:
            return Fail("账号不存在或者账号密码错误！")
        # 为用户生成一个唯一的Token
        user.token = str(uuid.uuid4().hex)
        user.save()
        ret_ser = LoginSerializer(instance=user)
        return Success(data=ret_ser.data, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def user_img_info_list(self, request, *args, **kwargs):
        """获取当前用户的图片信息"""
        username = self.request.user.username
        img_info = UserImgInfoSerializer(ImgInfo.objects.filter(username=username).all())
        return Success(data=img_info, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def user_img_info_retrieve(self, request, *args, **kwargs):
        """获取当前用户的图片信息详情"""
        img_id = self.kwargs.get("img_id")
        username = self.request.user.username
        img_info = UserImgInfoSerializer(ImgInfo.objects.filter(username=username, id=img_id).all())
        return Success(data=img_info, status=status.HTTP_200_OK)


USER_PATH = "USERRES"

IMG_INFO_PATH = "IMG_INFO"
