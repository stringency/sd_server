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

from SDTasks import views

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("api/<str:version>/paramtran/", views.ParamTranView.as_view({"get": "list", "post": "create"}),
         name='parameterTransmission'),
    path("api/<str:version>/paramtran/<str:pk>", views.ParamTranView.as_view({"get": "retrieve"}),
         name='parameterTransmissionDetail'),
    path("api/<str:version>/paramtranTMP/", views.ParamTranViewTMP.as_view({"get": "list", "post": "create"}),
         name='parameterTransmissionTMP'),
]
