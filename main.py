import os
import time
from speech import Speech_Recognition, Speech_Synthesizer, Speech_Waken
import qwen
from config import config



# 生成配置文件

if not os.path.exists('./config/config.ini'):
    if not os.path.exists('./config'):
        os.mkdir('./config')
    config.generate_config_file()
# 读取配置文件
print('正在读取配置文件...')
config.read_config_file()
manager=qwen.BookkeepingManager()
while True:
    Speech_Waken.speech_recognize_keyword_locally_from_microphone()
    Speech_Synthesizer.start('唉！我在！')
    Speech_Recognition.start()
    print('等待语音输入中...')
    while True:
        if Speech_Recognition.start_time is not None and time.time() - Speech_Recognition.start_time > 30:
            Speech_Recognition.stop()
            Speech_Recognition.start()
        Speech_Recognition.send_audio_frame()   # 从流中读取音频数据，并将其发送给识别服务。
        if Speech_Recognition.last_voice_time is not None and time.time() - Speech_Recognition.last_voice_time > 1:     # 判断停顿时间断句
            print('你说：', Speech_Recognition.latest_sentence)
            if Speech_Recognition.last_voice_time is not None:
                Speech_Recognition.stop()
            Speech_Synthesizer.start(qwen.get_qwen_response_parallel(manager, Speech_Recognition.latest_sentence))     # 调用语音合成 合成从千问获取的回答
            print('对话结束，程序重新开始...')
            break

