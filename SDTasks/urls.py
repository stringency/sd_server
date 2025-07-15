from rest_framework.routers import DefaultRouter

from SDTasks import views

router = DefaultRouter(trailing_slash=True)
urlpatterns = []

router.register(r"txt2img", views.Txt2ImgView, basename="txt2img")
router.register(r"taskinfo", views.TaskInfoView, basename="taskinfo")
router.register(r"imgprogress", views.ImgProgressView, basename="imgprogress")
router.register(r"img2img", views.Img2ImgView, basename="img2img")

urlpatterns += router.urls
