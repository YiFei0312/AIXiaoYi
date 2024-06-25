import os
import time
import Speech_Synthesizer
import Speech_Recognition
import qwen
import config

if not os.path.exists('./config.ini'):
    config.generate_config_file()
config.read_config_file()
Speech_Recognition.start()
manager=qwen.BookkeepingManager()
while True:
    if Speech_Recognition.start_time is not None and time.time() - Speech_Recognition.start_time > 30:
        Speech_Recognition.stop()
        Speech_Recognition.start()
    print('等待语音输入...')
    Speech_Recognition.send_audio_frame()   # 从流中读取音频数据，并将其发送给识别服务。
    if Speech_Recognition.last_voice_time is not None and time.time() - Speech_Recognition.last_voice_time > 1:     # 判断停顿时间断句
        print('记录下完整语音：', Speech_Recognition.latest_sentence)
        if Speech_Recognition.last_voice_time is not None:
            Speech_Recognition.stop()
        Speech_Synthesizer.start(qwen.get_qwen_response_parallel(manager,Speech_Recognition.latest_sentence))     # 调用语音合成 合成从千问获取的回答
        Speech_Recognition.start()
        print('对话结束，程序重新开始...')
