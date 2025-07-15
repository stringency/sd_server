from .celery import app as celery_app

__all__ = ['celery_app']
# 终端启动worker,并以协程方式运作
# celery -A sd_server worker -l info -P eventlet
# 终端启动beat定时任务
# celery -A sd_server beat -l info
