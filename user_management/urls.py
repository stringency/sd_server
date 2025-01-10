from rest_framework.routers import DefaultRouter

from user_management import views

router = DefaultRouter(trailing_slash=True)
urlpatterns = []

router.register(r"user_management/user_info", views.UserInfoView, basename="user_info")

urlpatterns += router.urls