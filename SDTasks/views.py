import json
import requests
import pika
from celery.result import AsyncResult
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from openai import OpenAI, AssistantEventHandler

from SDTasks.serializers import ParamTranSerializer

from SDTasks.tasks import process_parameters


# Create your views here.


class Txt2ImgTMPView(GenericViewSet):
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
        try:
            # 将参数传递给SDAPI
            response = requests.post('http://127.0.0.1:7860/sdapi/v1/txt2img', json=parameters)
            response.raise_for_status()
            # 返回SDAPI生成的图片或其他结果
            return Response(response.json(), status=status.HTTP_200_OK)
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
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        parameters = request.data  # 获取处理后的参数
        print(parameters)

        try:
            # 将参数传递给SDAPI
            response = requests.post('http://127.0.0.1:7860/sdapi/v1/img2img', json=parameters)
            response.raise_for_status()
            # 返回SDAPI生成的图片或其他结果
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Txt2ImgView(GenericViewSet):
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
