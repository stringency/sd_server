import os
from celery import Celery

# 1. 导入django配置; 后续便于使用django组件功能
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sd_server.settings')

# 2. 实例化celery对象
app = Celery('sd_server')

# 3. 从django配置文件中导入celery相关的配置; 如果添加 namespace='CELERY' 参数,则celery的配置参数需要添加 "CELERY_" 的前缀
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. 在django所有应用中自动搜索 tasks.py 文件, 作为任务文件
app.autodiscover_tasks()
