import base64
import os
import time
import uuid
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image
from celery import shared_task

from SDTasks.models import ImgInfo
from user_management.models import UserInfo


@shared_task
def add(x, y):
    return x + y


# 定义任务函数
@shared_task
def send_email(user):
    time.sleep(2)
    return f'发送邮件成功:{user}'


USER_PATH = "USERRES"

IMG_INFO_PATH = "IMG_INFO"
# 动态获取当前项目的绝对路径
IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), USER_PATH, IMG_INFO_PATH)

THUMBNAIL_SIZE = (128, 128)  # 生成缩略图的尺寸


@shared_task(bind=True)
def generate_image(self, username, parameters, img_type):
    """
    Celery 任务：调用 SDAPI 生成图像
    """
    n_iter = int(parameters.get("n_iter", 1))  # 获取需要生成的图片数量
    IMG_PATH_USER = os.path.join(IMG_PATH, username)
    os.makedirs(IMG_PATH_USER, exist_ok=True)

    # 获取用户对象（如果用户存在）
    user_obj = UserInfo.objects.filter(username=username).first()

    # **提前创建 n_iter 个数据库记录**
    img_records = []
    try:
        for _ in range(n_iter):
            file_name = f"{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            file_path = os.path.join(IMG_PATH_USER, file_name)

            img_info = ImgInfo.objects.create(
                img_path=file_path,  # 先存文件路径
                img_logo=None,  # 先不存缩略图
                username=user_obj,
                img_type=img_type,
                img_name=file_name,
                img_status=ImgInfo.PENDING,  # 标记为 "正在生图"
                desc="正在生成图片...",
                task_id=self.request.id
            )
            img_records.append(img_info)

        # **调用 SDAPI 生成图像**
        url = 'http://127.0.0.1:7860/sdapi/v1/txt2img' if img_type == ImgInfo.TXTTOIMG else 'http://127.0.0.1:7860/sdapi/v1/img2img'

        response = requests.post(url, json=parameters)
        response.raise_for_status()
        json_data = response.json()
        images = json_data.get('images', [])

        if len(images) != n_iter:
            IMG_PATH_ERROR = os.path.join(IMG_PATH, "error")
            os.makedirs(IMG_PATH_ERROR, exist_ok=True)
            for index, img_data in enumerate(images):
                file_name = f"{index}.png"
                IMG_PATH_ERROR_index = os.path.join(IMG_PATH_ERROR, file_name)
                img_bytes = base64.b64decode(img_data)
                img = Image.open(BytesIO(img_bytes))
                img.save(IMG_PATH_ERROR_index)  # 保存原图
            if img_type == ImgInfo.IMGTOIMG:
                images = images[:-1]
            else:
                raise ValueError(f"请求 {n_iter} 张图片，但 SDAPI 返回了 {len(images)} 张")

        # **逐个更新数据库记录**
        for img_info, img_data in zip(img_records, images):
            img_bytes = base64.b64decode(img_data)
            img = Image.open(BytesIO(img_bytes))
            img.save(img_info.img_path)  # 保存原图

            # **生成缩略图**
            img.thumbnail(THUMBNAIL_SIZE)
            thumb_io = BytesIO()
            img.save(thumb_io, format="PNG", quality=70)
            thumb_bytes = thumb_io.getvalue()

            # **更新数据库记录**
            img_info.img_logo = thumb_bytes
            img_info.img_status = ImgInfo.SUCCESS  # 标记为 "生图完成"
            img_info.desc = "生图完成"
            img_info.save(update_fields=["img_logo", "img_status", "desc"])

        return {"status": "success", "json_data": json_data}

    except Exception as e:
        # **如果失败，所有图片记录都更新为 failure**
        for img_info in img_records:
            img_info.img_status = "failure"
            img_info.desc = str(e)
            img_info.save(update_fields=["img_status", "desc"])

        return {"status": "error", "message": str(e)}
