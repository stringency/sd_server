"""
URL configuration for sd_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

import SDTasks.views
import GPTBot.views

schema_view = get_schema_view(
    openapi.Info(
        title="CarmiSystem API接口文档",
        default_version='1.0',
        description="描述信息",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="1422699629@qq.com"),
        license=openapi.License(name="协议版本"),
    ),
    public=True,
    # authentication_classes=[],
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    # path("admin/", admin.site.urls),
    # 接口文档
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # SDTasks接口
    path("api/<str:version>/paramtran/", SDTasks.views.ParamTranView.as_view({"get": "list", "post": "create"}),
         name='parameterTransmission'),
    path("api/<str:version>/paramtran/<str:pk>", SDTasks.views.ParamTranView.as_view({"get": "retrieve"}),
         name='parameterTransmissionDetail'),
    path("api/<str:version>/paramtranTMP/", SDTasks.views.ParamTranViewTMP.as_view({"get": "list", "post": "create"}),
         name='parameterTransmissionTMP'),
    # GPTBot接口
    path("api/<str:version>/gptbot/", GPTBot.views.GptBot.as_view({"post": "create"}),
         name='GPTBot'),
]
