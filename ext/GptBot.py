from openai import OpenAI
from openai import AssistantEventHandler

client = OpenAI()


# 创建事件处理程序类
class EventHandler(AssistantEventHandler):
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


# 初始化对话线程
thread = client.beta.threads.create()

# 对话循环
while True:
    # 用户输入
    user_input = input("\nuser > ")

    if user_input.lower() in ['exit', 'quit']:
        print("Exiting conversation.")
        break

    # 发送用户消息
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # 使用流式输出助手的回应
    with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id='',
            instructions="Please address the user as Master. The user has a premium account.\n",
            event_handler=EventHandler(),
    ) as stream:
        stream.until_done()
