import threading

import pyaudio
from dashscope.audio.asr import (Recognition, RecognitionCallback,
                                 RecognitionResult)
import time


class Recognizer:
    def __init__(self):
        print("初始化语音识别器")
        self.mic = None
        self.stream = None
        self.latest_sentence = ''
        self.display_text = ''
        self.max_chars = 40
        self.clear_flag = False
        self.last_voice_time = None
        self.start_time = None
        self.callback = self.Callback(self)  # 传递外部类实例
        self.recognition = Recognition(model='paraformer-realtime-v2',
                                       format='pcm',
                                       sample_rate=16000,
                                       callback=self.callback)

    class Callback(RecognitionCallback):
        def __init__(self, parent):
            print("初始化回调函数")
            super().__init__()
            self.parent = parent  # 保存外部类实例的引用

        def on_open(self):
            print("语音识别器打开")
            self.parent.mic = pyaudio.PyAudio()
            self.parent.stream = self.parent.mic.open(format=pyaudio.paInt16,
                                                      channels=1,
                                                      rate=16000,
                                                      input=True)
            self.parent.start_time = time.time()

        def on_close(self):
            print("语音识别器关闭")
            if self.parent.stream:
                self.parent.stream.stop_stream()
                self.parent.stream.close()
            if self.parent.mic:
                self.parent.mic.terminate()
            self.parent.stream = None
            self.parent.mic = None
            self.parent.last_voice_time = None
            self.parent.start_time = None
            self.parent.display_text = ''

        def on_event(self, result: RecognitionResult):
            print("语音识别器事件")
            sentence = result.get_sentence()
            is_end = result.is_sentence_end(sentence)

            if len(self.parent.display_text) > 0 or self.parent.clear_flag:
                print('\033[1A\033[K', end='')
                if self.parent.clear_flag:
                    self.parent.clear_flag = False
                    self.parent.display_text = ''
                    self.parent.latest_sentence = ''

            self.parent.display_text = sentence['text']
            if is_end:
                self.parent.latest_sentence = self.parent.display_text
                if len(self.parent.display_text) > self.parent.max_chars:
                    self.parent.clear_flag = True
            self.parent.last_voice_time = time.time()

    def start(self):
        self.recognition.start()
        print("语音识别器启动成功")

    def stop(self):
        self.recognition.stop()

    def send_audio_frame(self):

        if self.stream:
            print("发送音频帧")
            data = self.stream.read(3200, exception_on_overflow=False)
            self.recognition.send_audio_frame(data)

    def speech_recognize(self):
        self.start()
        print("等待语音输入中...")
        # logger.info('等待语音输入中...')
        while True:
            if self.start_time is not None and time.time() - self.start_time > 30:
                self.stop()
                self.start()
            try:
                self.send_audio_frame()
            except Exception as e:
                print(1, e)
                # logger.error(f"发送音频帧失败: {e}")
                break

            if self.last_voice_time is not None and time.time() - self.last_voice_time > 1:
                # logger.info(f"你说：{speech_recognizer.latest_sentence}")
                if self.last_voice_time is not None:
                    self.stop()
                try:
                    user_say = self.latest_sentence
                    return user_say
                except Exception as e:
                    print(e)
                    # logger.error(f"识别语音失败: {e}")
