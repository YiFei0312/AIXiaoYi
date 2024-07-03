import json
from http import HTTPStatus
import dashscope
import http.client
import tool
from config import config
from concurrent.futures import ThreadPoolExecutor

class BookkeepingManager:
    TOOL_MAP = tool.TOOL_MAP
    TOOL_MAP_1 = tool.TOOL_MAP_1

    def __init__(self):
        self.ai_bookkeeping = [{'role': 'system', 'content': config.personality['default']}]

    def get_qwen_response_serial(self, mess: str):  # 串行请求
        try:
            response = dashscope.Generation.call(model="qwen-max",
                                                 messages=[{'role': 'system', 'content': '你是一个负责判断是否使用工具的助手'}, {'role': 'user', 'content': mess}],
                                                 tools=tool.tools,
                                                 result_format='message')
            if response.status_code == http.client.OK:
                assistant_message = response.output.choices[0]['message']
                if 'tool_calls' in response.output.choices[0].message:
                    tool_name = response.output.choices[0].message.tool_calls[0]['function']['name']
                    if tool_name in self.TOOL_MAP:
                        tool_message = self.TOOL_MAP[tool_name]()
                        self.add_conversation('user', mess)
                        self.add_conversation(assistant_message['role'], tool_message)
                        return tool_message
                    elif tool_name in self.TOOL_MAP_1:
                        description = \
                        json.loads(response.output.choices[0].message.tool_calls[0]['function']['arguments'])[
                            'description']
                        tool_message = tool.draw_picture(description)
                        self.add_conversation('user', mess)
                        self.add_conversation(assistant_message['role'], tool_message)
                        return tool_message
                else:
                    self.add_conversation('user', mess)
                    response = dashscope.Generation.call(model="qwen-max",
                                                         messages=self.ai_bookkeeping,
                                                         result_format='message')
                    if response.status_code == http.client.OK:
                        assistant_message = response.output.choices[0]['message']  # 成功，添加assistant回复
                        print(assistant_message['content'])
                        self.add_conversation(assistant_message['role'], assistant_message['content'])
                        return assistant_message['content']
                    else:
                        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                            response.request_id, response.status_code,
                            response.code, response.message
                        ))  # 失败，打印错误信息并回滚最后一条消息
                        self.ai_bookkeeping = self.ai_bookkeeping[:-1]
            else:
                print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                    response.request_id, response.status_code,
                    response.code, response.message
                ))  # 失败，打印错误信息

        except Exception as e:
            print(f'Exception occurred: {e}')

    def clear_request(self):
        """清空对话记录"""
        self.ai_bookkeeping = [{'role': 'system', 'content': config.personality['default']}]

    def add_conversation(self, role, msg):
        self.ai_bookkeeping.append({
            'role': role,
            'content': msg
        })

    def get_tool_response(self, mess: str):  # 获取工具回复
        response = dashscope.Generation.call(model="qwen-max",
                                             messages=[{'role': 'system', 'content': '你是一个负责判断是否使用工具的助手'}, {'role': 'user', 'content': mess}],
                                             tools=tool.tools,
                                             result_format='message')
        if response.status_code == http.client.OK:
            assistant_message = response.output.choices[0]['message']
            if 'tool_calls' in response.output.choices[0].message:
                tool_name = response.output.choices[0].message.tool_calls[0]['function']['name']
                if tool_name in self.TOOL_MAP:
                    tool_message = self.TOOL_MAP[tool_name]()
                    # self.add_conversation('user', mess)
                    # self.add_conversation(assistant_message['role'], tool_message)
                    return [tool_message, assistant_message['role']]
                elif tool_name in self.TOOL_MAP_1:
                    description = json.loads(response.output.choices[0].message.tool_calls[0]['function']['arguments'])[
                        'description']
                    tool_message = tool.draw_picture(description)
                    # self.add_conversation('user', mess)
                    # self.add_conversation(assistant_message['role'], tool_message)
                    return [tool_message, assistant_message['role']]
            else:
                return
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))  # 失败，打印错误信息

    def get_response(self, mess: str):  # 多轮对话回复
        self.add_conversation('user', mess)
        response = dashscope.Generation.call(model="qwen-max",
                                             messages=self.ai_bookkeeping,
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


def get_qwen_response_parallel(manger: BookkeepingManager, mess: str):  # 多线程请求
    with ThreadPoolExecutor() as executor:
        ftool = executor.submit(manger.get_tool_response, mess)
        future = executor.submit(manger.get_response, mess)
    if ftool.result() == None:
        print(future.result())
        return future.result()
    else:
        manger.ai_bookkeeping = manger.ai_bookkeeping[:-1]
        manger.add_conversation(ftool.result()[1], ftool.result()[0])
        return ftool.result()[0]
