from .musicplayer import *
from .adjust_voice import *
from .vision import *
from .time import *
import sqlite3
conn = sqlite3.connect('config.db')
c = conn.cursor()
c.execute('SELECT * FROM tools')
tools_from_db = c.fetchall()
tools = []
for row in tools_from_db:
    c.execute(f'SELECT * FROM parameters WHERE tool_id = {row[0]}')
    properties_list = c.fetchall()
    properties = []
    required_properties = []
    for property in properties_list:
        properties.append({
            property[2]: {
                "type": property[3],
                "description": property[4]
            }
        })
        required_properties.append(property[2])
    tool = {
        "type": row[3],
        "function": {
            "name": row[1],
            "description": row[2],
            "parameters": {
                'type': "object",
                'properties': properties,
            },
            "required": required_properties
        }
    }
    tools.append(tool)
c.close()
conn.close()

# # 定义工具列表，模型在选择使用哪个工具时会参考工具的name和description
# tools = [
#     # 工具1 拍摄一张图片来识别
#     {
#         "type": "function",
#         "function": {
#             "name": "identify_images",
#             "description": "当问你看到了什么时，你可以使用这个工具。",
#             "parameters": {}  # 因为无需输入参数，因此parameters为空字典
#         }
#     },
#     # 工具2 拍摄当前的图片保存下来
#     {
#         "type": "function",
#         "function": {
#             "name": "take_photo",
#             "description": "当让你记下现在看到的东西或者拍摄当前的场景或者拍一张照片时，你可以使用这个工具。",
#             "parameters": {}  # 因为无需输入参数，因此parameters为空字典
#         }
#     },
#     # 工具3 绘制图片
#     {
#         "type": "function",
#         "function": {
#             "name": "draw_picture",
#             "description": "当你想根据用户描述绘制图片时，你可以使用这个工具。",
#             "parameters": {  # 用户描述想要绘制的图片，因此参数设置为description
#                 "type": "object",
#                 "properties": {
#                     "description": {
#                         "type": "string",
#                         "des": "转换成英文的用户对绘制图片的描述。"
#                     }
#                 }
#             },
#             "required": [
#                 "des"
#             ]
#         }
#     },
#     # 工具4 获取当前时间
#     {
#         "type": "function",
#         "function": {
#             "name": "get_current_time",
#             "description": "当用户想要获取当前时间，或者用户问你现在几点了时，你可以使用这个工具。",
#             "parameters": {}  # 因为无需输入参数，因此parameters为空字典
#         }
#     },
#
#     # 工具5 播放音乐
#     {
#         "type": "function",
#         "function": {
#             "name": "play_music",
#             "description": "当用户想要播放音乐时，你可以使用这个工具。",
#             "parameters": {  # 用户描述想要绘制的图片，因此参数设置为description
#                 "type": "object",
#                 "properties": {
#                     "description": {
#                         "type": "string",
#                         "des": "用户想要播放歌曲的名称。"
#                     }
#                 }
#             },
#             "required": [
#                 "des"
#             ]
#         }
#     },
#     # 工具6 暂停音乐
#     {
#         "type": "function",
#         "function": {
#             "name": "pause_music",
#             "description": "当用户想要暂停音乐或者歌曲时，你可以使用这个工具。",
#             "parameters": {}  # 因为无需输入参数，因此parameters为空字典
#         }
#     },
#     # 工具7 恢复音乐
#     {
#         "type": "function",
#         "function": {
#             "name": "resume_music",
#             "description": "当用户想要恢复音乐或者歌曲时，你可以使用这个工具。",
#             "parameters": {}  # 因为无需输入参数，因此parameters为空字典
#         }
#     },
#
#     # 工具8 停止音乐
#     {
#         "type": "function",
#         "function": {
#             "name": "stop_music",
#             "description": "当用户想要停止音乐或者歌曲时，你可以使用这个工具。",
#             "parameters": {}  # 因为无需输入参数，因此parameters为空字典
#         }
#     },
#     # 工具9 调节音量
#     {
#         "type": "function",
#         "function": {
#             "name": "adjust_volume",
#             "description": "当用户想要调节音量时，你可以使用这个工具。",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "description": {
#                         "type": "int",
#                         "des": "用户想要调节音量的大小，取值为-100到100"
#                     }
#                 }
#             },
#             "required": [
#                 "des"
#             ]
#         }
#     },
#
#     # 工具10 设置音量
#     {
#         "type": "function",
#         "function": {
#             "name": "set_volume",
#             "description": "当用户想要设置音量时，你可以使用这个工具。",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "description": {
#                         "type": "int",
#                         "des": "用户想要设置音量的数值，取值为0到100。"
#                     }
#                 }
#             },
#             "required": [
#                 "des"
#             ]
#         }
#     },
# ]




TOOL_MAP = {
    'identify_images': identify_images,  # 1识别图像
    'take_photo': take_photo,  # 2拍照
    'get_current_time': get_current_time,  # 3获取当前时间
    'pause_music': pause_music,  # 4暂停音乐
    'resume_music': resume_music,  # 5恢复音乐
    'stop_music': stop_music,  # 6停止音乐
    'draw_picture': draw_picture,  # 7画图'
    'play_music': play_music,  # 8播放音乐
    'adjust_volume': adjust_volume,  # 9调节音量
    'set_volume': set_volume,  # 10设置音量
}

