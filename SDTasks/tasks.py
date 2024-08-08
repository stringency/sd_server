from celery import shared_task
from celery.utils.log import get_task_logger
import json
from kombu import Exchange, Queue, Connection

# celery -A sd_server worker -l info


logger = get_task_logger(__name__)

@shared_task
def process_parameters(parameters):
    try:
        # 将参数转换为JSON字符串并编码为字节
        message_body = json.dumps(parameters)
        # Celery任务用于发送消息

        connection = Connection('amqp://guest:guest@localhost:5672//')
        exchange = Exchange('parameter_exchange', type='topic', durable=True)
        with connection.Producer() as producer:
            producer.publish(
                message_body,
                exchange='parameter_exchange',
                routing_key='parameters.key',
                declare=[exchange],
                delivery_mode=2  # 设置消息持久化
            )

    except Exception as e:
        # 处理连接错误或其他异常
        logger.error(f"Error in process_parameters task: {e}")

