import json
import requests
import pika


def callback(ch, method, properties, body):
    try:
        # 处理消息的代码在这里
        print("Received message:", body)
        # 将消息转换为JSON
        parameters = json.loads(body)

        # 发送HTTP请求到SDAPI
        response = requests.post('http://127.0.0.1:7860/sdapi/v1/txt2img', json=parameters)
        # 手动确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)

        if response.status_code == 200:
            result = response.json()
            print("Result from SDAPI:", result)
            # 可以在这里将结果发送回另一个队列或者处理结果
            # 连接到RabbitMQ
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()

            # 声明交换机
            channel.exchange_declare(
                exchange='res_exchange',
                exchange_type='topic',
                # durable=True
            )

            # 将消息发送到交换机
            channel.basic_publish(
                exchange='res_exchange',
                routing_key='sd_res',
                body=json.dumps(result).encode('utf-8'),
                # properties=pika.BasicProperties(delivery_mode=2)  # 设置消息持久化
            )

            # 关闭连接
            connection.close()
        else:
            print(f"Error from SDAPI: {response.status_code} - {response.text}")


    except Exception as e:
        print(f"Failed to process message: {e}")
        # 如果消息处理失败，可以选择不确认，以便消息重新投递
        # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def consume_parameters():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(
            exchange='param_exchange',
            exchange_type='topic',
            # durable=True
        )
        # 创建队列
        result = channel.queue_declare("", exclusive=True)
        queue_name = result.method.queue
        print("Queue name:", queue_name)
        # 队列绑定到交换机
        channel.queue_bind(exchange='param_exchange', queue=queue_name, routing_key='sd')

        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False  # 不自动确认消息，在回调时候手动确认
        )

        print("Waiting for message... To exit press Ctrl+C")
        channel.start_consuming()
    except Exception as e:
        print(f"Error in consume_parameters task: {e}")


if __name__ == '__main__':
    consume_parameters()
