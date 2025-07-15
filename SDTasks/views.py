import asyncio
import base64
import json
import os
import uuid
from datetime import datetime
from io import BytesIO

import requests
import pika
from PIL import Image
from celery.result import AsyncResult
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from openai import OpenAI, AssistantEventHandler

from GPTBot.utils import translate_assistant, dp_online_translate_assistant
from SDTasks.serializers import ParamTranSerializer

from SDTasks.tasks import process_parameters
from ext.Img2MaskPIL import generate_mask_PIL
from ext.sdtext_add_wb import sd_add_text
from ext.text_add_b import add_black_text

from .celery_task import generate_image
from .models import ImgInfo

USER_PATH = "USERRES"

IMG_INFO_PATH = "IMG_INFO"
# 动态获取当前项目的绝对路径
IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), USER_PATH, IMG_INFO_PATH)


# print(IMG_PATH)
# parameters.update({'save_images': True})
# parameters['alwayson_scripts'].update({'custom_save_script': {'args': [IMG_PATH]}})  # 设定图片保存位置


class Txt2ImgView(GenericViewSet):
    """
    文生图
    只能本地展示,负责转接参数到SDAPI
    """
    # authentication_classes = []
    # permission_classes = [AllowAny]
    serializer_class = ParamTranSerializer

    # def list(self, request, *args, **kwargs):
    # """
    # 生图过程
    # :param request:
    # :param args:
    # :param kwargs:
    # :return:
    # """
    # # 这里可以修改参数，例如增加或修改请求参数
    #
    # # 将修改后的参数重新构建URL或请求
    # url = f"http://127.0.0.1:7860/sdapi/v1/progress?skip_current_image=false"
    #
    # try:
    #     # 发送请求到SDAPI
    #     response = requests.get(url)
    #     response.raise_for_status()
    #     return Response(response.json(), status=status.HTTP_200_OK)
    # except requests.exceptions.RequestException as e:
    #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """
        提交 Celery 任务，返回任务 ID
        """
        parameters = request.data  # 获取参数
        print(parameters["prompt"])
        parameters["prompt"] = dp_online_translate_assistant(parameters["prompt"])
        print(parameters["prompt"])
        img_type = ImgInfo.TXTTOIMG
        task = generate_image.delay(self.request.user.username, parameters, img_type)  # 异步提交任务
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
        # """
        # 生图接口调用
        # :param request:
        # :param args:
        # :param kwargs:
        # :return:
        # """
        # parameters = request.data  # 获取处理后的参数
        # # print(parameters)
        # # parameters['alwayson_scripts']['controlnet']['args'][0]['image'], textIndex = add_black_text() # 创建文字图片
        # # print(parameters['alwayson_scripts']['controlnet']['args'][0]['image'])
        # try:
        #     # 将参数传递给SDAPI
        #     response = requests.post('http://127.0.0.1:7860/sdapi/v1/txt2img', json=parameters)
        #     response.raise_for_status()
        #     # print(response.json()['info'])
        #     # 字符串转json，获取seed
        #     print(json.loads(response.json()['info'])["seed"])
        #     # 修改response响应里面的字段
        #     # images字段
        #     # print("改变前:", response.json()['images'])
        #     response_alter = response.json()
        #
        #     # 保存图片
        #     if response.status_code == 200:
        #         # 解析返回的 JSON 数据
        #         json_data = response.json()
        #         images = json_data['images']  # 获取生成的图像Base64编码数组
        #
        #         # 指定保存路径
        #         # output_dir = IMG_PATH  # 保存图片的目录
        #         os.makedirs(IMG_PATH, exist_ok=True)  # 如果目录不存在，则创建
        #
        #         # 处理每张图片
        #         for i, img_data in enumerate(images):
        #             img_bytes = base64.b64decode(img_data)  # 将Base64数据解码为字节流
        #             img = Image.open(BytesIO(img_bytes))  # 将字节流转换为PIL图像对象
        #
        #
        #             # 生成随机字符串和时间戳
        #             random_str = uuid.uuid4().hex[:8]  # 生成8位随机字符串
        #             timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # 当前时间戳
        #
        #             # 保存图片到指定目录
        #             output_path = os.path.join(IMG_PATH, f"{random_str}_{timestamp}.png")
        #             img.save(output_path)  # 保存图片
        #             # print(f"图片已保存到: {output_path}")
        #
        #             # 显示图片（可选）
        #             # img.show()
        #     # response_alter["images"] = sd_add_text(response.json()['images'], textIndex) # 加入文字图片
        #     # print("对比:", sd_add_text(response.json()['images'], textIndex))
        #     # print("改变后:", response.json()['images'])
        #
        #     # 返回SDAPI生成的图片或其他结果
        #     return Response(response_alter, status=status.HTTP_200_OK)
        # except requests.exceptions.RequestException as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # def retrieve(self, request, *args, **kwargs):
        #     """
        #     查询任务状态或获取结果
        #     """
        #     task_id = request.query_params.get("task_id")
        #     if not task_id:
        #         return Response({"error": "任务 ID 不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        #
        #     task_result = AsyncResult(task_id)
        #
        #     if task_result.state == "PENDING":
        #         return Response({"status": "PENDING"}, status=status.HTTP_202_ACCEPTED)
        #     elif task_result.state == "FAILURE":
        #         return Response({"status": "FAILURE", "error": str(task_result.result)},
        #                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        #     elif task_result.state == "SUCCESS":
        #         return Response({"status": "SUCCESS", "images": task_result.result["json_data"]}, status=status.HTTP_200_OK)
        #     else:
        #         return Response({"status": task_result.state}, status=status.HTTP_202_ACCEPTED)

    # @action(methods=["get"], detail=False)
    # def img_progress(self, request, *args, **kwargs):
    #     """
    #     生图过程
    #     :param request:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     # 这里可以修改参数，例如增加或修改请求参数
    #
    #     # 将修改后的参数重新构建URL或请求
    #     url = f"http://127.0.0.1:7860/sdapi/v1/progress?skip_current_image=false"
    #
    #     try:
    #         # 发送请求到SDAPI
    #         response = requests.get(url)
    #         response.raise_for_status()
    #         return Response(response.json(), status=status.HTTP_200_OK)
    #     except requests.exceptions.RequestException as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskInfoView(GenericViewSet):
    """
    查看工单任务情况
    """

    def list(self, request, *args, **kwargs):
        """
        查询任务状态或获取结果
        """
        task_id = request.query_params.get("task_id")
        # print(self.request.user.username)
        if not task_id:
            return Response({"error": "任务 ID 不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        task_result = AsyncResult(task_id)

        if task_result.state == "PENDING":
            return Response({"status": "PENDING"}, status=status.HTTP_202_ACCEPTED)
        elif task_result.state == "FAILURE":
            return Response({"status": "FAILURE", "error": str(task_result.result)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif task_result.state == "SUCCESS":
            return Response({"status": "SUCCESS", "images": task_result.result["json_data"]}, status=status.HTTP_200_OK)
        else:
            return Response({"status": task_result.state}, status=status.HTTP_202_ACCEPTED)


class ImgProgressView(GenericViewSet):
    """
    生图过程查询
    """

    def list(self, request, *args, **kwargs):
        """
        生图过程
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 这里可以修改参数，例如增加或修改请求参数

        # 将修改后的参数重新构建URL或请求
        url = f"http://127.0.0.1:7860/sdapi/v1/progress?skip_current_image=false"

        try:
            # 发送请求到SDAPI
            response = requests.get(url)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Img2ImgView(GenericViewSet):
    """
    图生图
    只能本地展示,负责转接参数到SDAPI
    """
    serializer_class = ParamTranSerializer

    # def create(self, request, *args, **kwargs):
    #     """
    #     提交 Celery 任务，返回任务 ID
    #     """
    #     parameters = request.data  # 获取参数
    #     parameters["mask"] = generate_mask_PIL(parameters["init_images"][0])
    #     print(parameters["mask"])
    #     parameters["prompt"] = dp_online_translate_assistant(parameters["prompt"])
    #     # print(parameters["prompt"])
    #     img_type = ImgInfo.IMGTOIMG
    #     task = generate_image.delay(self.request.user.username, parameters, img_type)  # 异步提交任务
    #     return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

    def create(self, request, *args, **kwargs):
        """
        提交 Celery 任务，返回任务 ID
        """
        return asyncio.run(self.process_request(request))

    async def async_generate_mask(self, image):
        """异步封装 generate_mask_PIL"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, generate_mask_PIL, image)

    async def async_translate_prompt(self, text):
        """异步封装 dp_online_translate_assistant"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, dp_online_translate_assistant, text)

    async def process_request(self, request):
        """处理请求的异步逻辑"""
        parameters = request.data
        init_image = parameters["init_images"][0]
        prompt = parameters["prompt"]

        # 并行执行两个任务
        mask, translated_prompt = await asyncio.gather(
            self.async_generate_mask(init_image),
            self.async_translate_prompt(prompt)
        )

        # 结果赋值
        parameters["mask"] = mask
        print(parameters["prompt"])
        parameters["prompt"] = translated_prompt
        print(parameters["prompt"])

        # 进入 Celery 任务
        img_type = ImgInfo.IMGTOIMG
        task = generate_image.delay(request.user.username, parameters, img_type)

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

    # def list(self, request, *args, **kwargs):
    #     # 这里可以修改参数，例如增加或修改请求参数
    #
    #     # 将修改后的参数重新构建URL或请求
    #     url = f"http://127.0.0.1:7860/sdapi/v1/progress?skip_current_image=false"
    #
    #     try:
    #         # 发送请求到SDAPI
    #         response = requests.get(url)
    #         response.raise_for_status()
    #
    #         # 保存图片
    #         if response.status_code == 200:
    #             # 解析返回的 JSON 数据
    #             json_data = response.json()
    #             images = json_data['images']  # 获取生成的图像Base64编码数组
    #
    #             # 指定保存路径
    #             # output_dir = IMG_PATH  # 保存图片的目录
    #             os.makedirs(IMG_PATH, exist_ok=True)  # 如果目录不存在，则创建
    #
    #             # 处理每张图片
    #             for i, img_data in enumerate(images):
    #                 img_bytes = base64.b64decode(img_data)  # 将Base64数据解码为字节流
    #                 img = Image.open(BytesIO(img_bytes))  # 将字节流转换为PIL图像对象
    #
    #                 # 生成随机字符串和时间戳
    #                 random_str = uuid.uuid4().hex[:8]  # 生成8位随机字符串
    #                 timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # 当前时间戳
    #
    #                 # 保存图片到指定目录
    #                 output_path = os.path.join(IMG_PATH, f"{random_str}_{timestamp}.png")
    #                 img.save(output_path)  # 保存图片
    #                 # print(f"图片已保存到: {output_path}")
    #
    #         return Response(response.json(), status=status.HTTP_200_OK)
    #     except requests.exceptions.RequestException as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def create(self, request, *args, **kwargs):
    #     parameters = request.data  # 获取处理后的参数
    #     parameters["mask"] = generate_mask_PIL(parameters["init_images"][0])
    #
    #     try:
    #         # 将参数传递给SDAPI
    #         response = requests.post('http://127.0.0.1:7860/sdapi/v1/img2img', json=parameters)
    #         response.raise_for_status()
    #         print(json.loads(response.json()['info'])["seed"])
    #         # print(response.json())
    #         # 返回SDAPI生成的图片或其他结果
    #         return Response(response.json(), status=status.HTTP_200_OK)
    #     except requests.exceptions.RequestException as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Txt2ImgTMPView(GenericViewSet):
    """
    文生图
    只能本地展示,负责转接参数到SDAPI
    """
    authentication_classes = []
    serializer_class = ParamTranSerializer

    def list(self, request, *args, **kwargs):
        # 这里可以修改参数，例如增加或修改请求参数

        # 将修改后的参数重新构建URL或请求
        url = f"http://127.0.0.1:7860/sdapi/v1/progress?skip_current_image=false"

        try:
            # 发送请求到SDAPI
            response = requests.get(url)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        parameters = request.data  # 获取处理后的参数
        # print(parameters)
        # parameters['alwayson_scripts']['controlnet']['args'][0]['image'], textIndex = add_black_text() # 创建文字图片
        # print(parameters['alwayson_scripts']['controlnet']['args'][0]['image'])
        try:
            # 将参数传递给SDAPI
            response = requests.post('http://127.0.0.1:7860/sdapi/v1/txt2img', json=parameters)
            response.raise_for_status()
            # print(response.json()['info'])
            # 字符串转json，获取seed
            print(json.loads(response.json()['info'])["seed"])
            # 修改response响应里面的字段
            # images字段
            # print("改变前:", response.json()['images'])
            response_alter = response.json()
            # response_alter["images"] = sd_add_text(response.json()['images'], textIndex) # 加入文字图片
            # print("对比:", sd_add_text(response.json()['images'], textIndex))
            # print("改变后:", response.json()['images'])

            # 返回SDAPI生成的图片或其他结果
            return Response(response_alter, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Img2ImgTMPView(GenericViewSet):
    """
    图生图
    只能本地展示,负责转接参数到SDAPI
    """
    serializer_class = ParamTranSerializer

    def list(self, request, *args, **kwargs):
        # 这里可以修改参数，例如增加或修改请求参数

        # 将修改后的参数重新构建URL或请求
        url = f"http://127.0.0.1:7860/sdapi/v1/progress?skip_current_image=false"

        try:
            # 发送请求到SDAPI
            response = requests.get(url)
            response.raise_for_status()

            # 保存图片
            if response.status_code == 200:
                # 解析返回的 JSON 数据
                json_data = response.json()
                images = json_data['images']  # 获取生成的图像Base64编码数组

                # 指定保存路径
                # output_dir = IMG_PATH  # 保存图片的目录
                os.makedirs(IMG_PATH, exist_ok=True)  # 如果目录不存在，则创建

                # 处理每张图片
                for i, img_data in enumerate(images):
                    img_bytes = base64.b64decode(img_data)  # 将Base64数据解码为字节流
                    img = Image.open(BytesIO(img_bytes))  # 将字节流转换为PIL图像对象

                    # 生成随机字符串和时间戳
                    random_str = uuid.uuid4().hex[:8]  # 生成8位随机字符串
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # 当前时间戳

                    # 保存图片到指定目录
                    output_path = os.path.join(IMG_PATH, f"{random_str}_{timestamp}.png")
                    img.save(output_path)  # 保存图片
                    # print(f"图片已保存到: {output_path}")

            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        parameters = request.data  # 获取处理后的参数
        parameters["mask"] = generate_mask_PIL(parameters["init_images"][0])

        try:
            # 将参数传递给SDAPI
            response = requests.post('http://127.0.0.1:7860/sdapi/v1/img2img', json=parameters)
            response.raise_for_status()
            print(json.loads(response.json()['info'])["seed"])
            # print(response.json())
            # 返回SDAPI生成的图片或其他结果
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Txt2ImgAnyTMPView(GenericViewSet):
    """
    文生图
    只能本地展示,负责转接参数到SDAPI
    """
    serializer_class = ParamTranSerializer

    def list(self, request, *args, **kwargs):
        # 这里可以修改参数，例如增加或修改请求参数

        # 将修改后的参数重新构建URL或请求
        url = f"http://127.0.0.1:7860/sdapi/v1/progress?skip_current_image=false"

        try:
            # 发送请求到SDAPI
            response = requests.get(url)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        parameters = request.data  # 获取处理后的参数
        # print(parameters)
        # parameters['alwayson_scripts']['controlnet']['args'][0]['image'], textIndex = add_black_text()
        # print(parameters['alwayson_scripts']['controlnet']['args'][0]['image'])
        try:
            # 将参数传递给SDAPI
            response = requests.post('http://127.0.0.1:7860/sdapi/v1/txt2img', json=parameters)
            response.raise_for_status()
            # print(response.json()['info'])
            # 字符串转json，获取seed
            print(json.loads(response.json()['info'])["seed"])
            # 修改response响应里面的字段
            # images字段
            # print("改变前:", response.json()['images'])
            response_alter = response.json()
            # response_alter["images"] = sd_add_text(response.json()['images'], textIndex)
            # print("对比:", sd_add_text(response.json()['images'], textIndex))
            # print("改变后:", response.json()['images'])

            # 返回SDAPI生成的图片或其他结果
            return Response(response_alter, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Txt2ImgView_celery(GenericViewSet):
    """
    能够线上部署的功能，利用消息队列操作
    优点：只要部署一个简单的传输参数的后端，算力交给个人电脑或者其他有算力的服务器
    失败：暂时无法解决消息队列与接口的对接
    """
    serializer_class = ParamTranSerializer
    result_data = None  # 类属性存储结果

    def callback(self, ch, method, properties, body):
        try:
            # 处理消息的代码在这里
            print("Received message:", body)
            # 将消息转换为JSON
            result = json.loads(body)
            print("Result from SDAPI:", result)
            # 存储结果
            Txt2ImgView.result_data = result

        except Exception as e:
            print(f"Failed to process message: {e}")
            # 如果消息处理失败，可以选择不确认，以便消息重新投递
            # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def list(self, request, *args, **kwargs):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.exchange_declare(
                exchange='res_exchange',
                exchange_type='topic',
                # durable=True
            )
            # 创建队列
            result = channel.queue_declare("", exclusive=True)
            queue_name = result.method.queue
            print("Queue name:", queue_name)
            # 队列绑定到交换机
            channel.queue_bind(exchange='res_exchange', queue=queue_name, routing_key='sd_res')

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.callback,
                auto_ack=False  # 不自动确认消息，在回调时候手动确认
            )

            print("Waiting for message... To exit press Ctrl+C")
            channel.start_consuming()
            # 返回处理后的结果
            if Txt2ImgView.result_data:
                return Response(Txt2ImgView.result_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No result available."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error in consume_parameters task: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        parameters = request.data
        try:
            # 连接到RabbitMQ
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()

            # 声明交换机
            channel.exchange_declare(
                exchange='param_exchange',
                exchange_type='topic',
                # durable=True
            )

            # 将消息发送到交换机
            channel.basic_publish(
                exchange='param_exchange',
                routing_key='sd',
                body=json.dumps(parameters).encode('utf-8'),
                # properties=pika.BasicProperties(delivery_mode=2)  # 设置消息持久化
            )

            # 关闭连接
            connection.close()

            return Response({"message": "Parameters received and sent to queue"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def create(self, request, *args, **kwargs):
    #     parameters = request.data  # 获取参数
    #     task = process_parameters.apply_async(args=[parameters])  # 异步执行任务
    #     return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)  # 返回任务id

    def retrieve(self, request, *args, **kwargs):
        task_id = kwargs['pk']
        task_result = AsyncResult(task_id)
        if task_result.state == 'PENDING':
            response = {'state': task_result.state, 'status': 'Pending...'}
        elif task_result.state != 'FAILURE':
            response = {
                'state': task_result.state,
                'result': task_result.result,
                'status': task_result.status
            }
        else:
            response = {
                'state': task_result.state,
                'status': str(task_result.info),  # this is the exception raised
            }
        return Response(response)
