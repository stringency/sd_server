from rest_framework import serializers

from user_management.models import (
    UserInfo,
)


class UserInfoSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password2 = serializers.CharField(write_only=True, required=False, label="确认密码")

    class Meta:
        model = UserInfo
        fields = ["username", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False}
        }

    def validate(self, attrs):
        request = self.context['request']  # 获取请求对象
        if request.method == 'POST':
            if not attrs.get("password"):
                raise serializers.ValidationError({"password": "密码是必填项"})
            if attrs.get("password") != attrs.pop("password2"):
                raise serializers.ValidationError({"password2": "两次密码输入不一致"})
        elif request.method in ['PUT', 'PATCH']:
            # 更新时无需校验 password 和 password2，但如果填写了，必须一致
            password = attrs.get("password")
            password2 = attrs.pop("password2", None)
            if password and password != password2:
                raise serializers.ValidationError({"password2": "两次密码输入不一致"})
        return attrs

    # def create(self, validated_data):
    #     # 创建用户时加密密码
    #     user = UserInfo.objects.create(
    #         username=validated_data["username"],
    #         password=validated_data["password"],  # 这里可以加密密码
    #     )
    #     return user

    def get_role(self, obj):
        return obj.get_role_display()

    # 自定义数据处理方法
    # def get_xxx(self, obj):
    #     return "name:
    # def get_status(self, obj):
    #     return obj.get_carmi_status_display()
