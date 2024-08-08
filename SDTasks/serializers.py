from rest_framework import serializers

from SDTasks import models


class ParamTranSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ParamInfo
        fields = "__all__"
