import cv2
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis, MultiModalConversation
import os
import datetime


def identify_images():
    if not os.path.exists('../data'):
        os.mkdir('../data')
    local_file_path = 'file://data/image.jpg'
    # 打开默认的摄像头
    camera = cv2.VideoCapture(0)

    # 捕获一帧图像
    ret, frame = camera.read()
    if not ret:
        print("无法捕获图像")
        return

    # 保存图像到当前工作目录
    image_path = "image.jpg"
    cv2.imwrite('../data/image.jpg', frame)

    # 释放摄像头资源
    camera.release()

    print(f"图像已保存至: {image_path}")
    messages = [{
        'role': 'system',
        'content': [{
            'text': 'You are a helpful assistant.'
        }]
    }, {
        'role':
            'user',
        'content': [
            {
                'image': local_file_path
            },
            {
                'text': '你看到了什么?'
            },
        ]
    }]
    response = MultiModalConversation.call(model='qwen-vl-max', messages=messages)
    print(response.output.choices[0].message.content[0]['text'])
    return response.output.choices[0].message.content[0]['text']


def take_photo():
    if not os.path.exists('../data'):
        os.mkdir('../data')
    # 获取当前时间并格式化为字符串
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    local_file_path = f"data/image_{current_time}.jpg"

    # 打开默认的摄像头
    camera = cv2.VideoCapture(0)

    # 捕获一帧图像
    ret, frame = camera.read()
    if not ret:
        print("无法捕获图像")
        return

    # 保存图像到当前工作目录，文件名为当前时间
    image_path = local_file_path
    cv2.imwrite(image_path, frame)

    # 释放摄像头资源
    camera.release()

    print(f"图像已保存至: {image_path}")
    return f'图片已记录下来了喵！'


def draw_picture(description):
    if not os.path.exists('../data'):
        os.mkdir('../data')
    rsp = ImageSynthesis.call(model='stable-diffusion-xl',
                              prompt=description,
                              negative_prompt="garfield",
                              n=1,
                              size='1024*1024')
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output)
        print(rsp.usage)
        # save file to current directory
        for result in rsp.output.results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
            with open('./data/%s' % file_name, 'wb+') as f:
                f.write(requests.get(result.url).content)
                return f'图片已保存下来了喵！'
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))
