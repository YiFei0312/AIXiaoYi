import json
import dashscope
import http.client
import tools
import config
from config import retry_on_failure
from concurrent.futures import ThreadPoolExecutor


class BookkeepingManager:
    TOOL_MAP = tools.TOOL_MAP
    def __init__(self):
        self.ai_bookkeeping = [{'role': 'system', 'content': config.personality}]


    def clear_request(self):
        """清空对话记录"""
        self.ai_bookkeeping = [{'role': 'system', 'content': config.personality}]

    def add_conversation(self, role, msg):
        self.ai_bookkeeping.append({
            'role': role,
            'content': msg
        })
    @retry_on_failure(max_retries=2, delay=2)
    def get_tool_response(self, mess: str):  # 获取工具回复
        response = dashscope.Generation.call(model="qwen-max",
                                             messages=[  # type: ignore
                                                 {'role': 'system',
                                                  'content': '你是一个负责判断是否使用工具的助手，你的任务就是判断用户的请求是否有调用工具函数的必要，和返回工具函数所需的参数。'},
                                                 {'role': 'user', 'content': mess},
                                             ],
                                             tools=tools.tools,
                                             result_format='message')
        if response.status_code == http.client.OK:
            assistant_message = response.output.choices[0]['message']
            if 'tool_calls' in response.output.choices[0].message:
                tool = response.output.choices[0].message.tool_calls[0]['function']
                tool_name = tool['name']
                property_list = json.loads(tool['arguments'])
                property_value = list(property_list.values())
                tool_message = self.TOOL_MAP[tool_name](*property_value)
                if tool_message is None:
                    tool_message = '工具调用成功。'
                return [tool_message, assistant_message['role']]
            else:
                return
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))  # 失败，打印错误信息
            tool_message = '请求工具失败'
            return [tool_message, 'assistant']
    @retry_on_failure(max_retries=2, delay=2)
    def get_response(self, mess: str):  # 多轮对话回复
        self.add_conversation('user', mess)
        response = dashscope.Generation.call(model="qwen-max",
                                             messages=self.ai_bookkeeping,  # type: ignore
                                             result_format='message')
        if response.status_code == http.client.OK:
            assistant_message = response.output.choices[0]['message']  # 成功，添加assistant回复
            self.add_conversation(assistant_message['role'], assistant_message['content'])
            return assistant_message['content']
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))  # 失败，打印错误信息并回滚最后一条消息
            self.ai_bookkeeping = self.ai_bookkeeping[:-1]

    def get_qwen_response_parallel(self, mess: str):  # 多线程请求
        with ThreadPoolExecutor() as executor:
            ftool = executor.submit(self.get_tool_response, mess)
            future = executor.submit(self.get_response, mess)
        if ftool.result() is None:
            print(future.result())
            return future.result()
        else:
            self.ai_bookkeeping = self.ai_bookkeeping[:-1]
            self.add_conversation(ftool.result()[1], ftool.result()[0])
            return ftool.result()[0]
