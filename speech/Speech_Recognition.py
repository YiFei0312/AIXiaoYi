import pyaudio
from dashscope.audio.asr import (Recognition, RecognitionCallback,
                                 RecognitionResult)
import time

mic = None
stream = None
latest_sentence: str = ''
display_text: str = ''
max_chars: int = 40
clear_flag: bool = False
last_voice_time = None  # 添加一个变量来记录上一次接收到语音的时间
start_time = None

class Callback(RecognitionCallback):
    def on_open(self) -> None:
        global mic
        global stream
        global start_time
        mic = pyaudio.PyAudio()
        stream = mic.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=16000,
                          input=True)
        last_voice_time = time.time()  # 在打开麦克风时初始化last_voice_time
        start_time = time.time()

    def on_close(self) -> None:
        global mic
        global stream
        global last_voice_time
        global display_text
        global latest_sentence
        stream.stop_stream()
        stream.close()
        mic.terminate()
        stream = None
        mic = None
        # print('程序识别完成正常退出！！！最后检测时间为：',last_voice_time)
        last_voice_time=None
        display_text = ''

    def on_event(self, result: RecognitionResult) -> None:
        global latest_sentence
        global display_text
        global max_chars
        global clear_flag
        global last_voice_time
        sentence = result.get_sentence()
        # print(sentence)
        is_end = result.is_sentence_end(sentence)
        # print(is_end)

        if len(display_text) > 0 or clear_flag:
            # clear the current row
            print('\033[1A\033[K', end='')
            if clear_flag:
                clear_flag = False
                display_text = ''
                latest_sentence = ''

        display_text = sentence['text']
        if is_end:
            latest_sentence = display_text
            if len(display_text) > max_chars:
                clear_flag = True
        # print(latest_sentence)
        last_voice_time = time.time()# 更新最后检测到语音的时间

callback = Callback()
recognition = Recognition(model='paraformer-realtime-v1',
                          format='pcm',
                          sample_rate=16000,
                          callback=callback)
def start():
    recognition.start()

def stop():
    recognition.stop()

def send_audio_frame():
    data = stream.read(3200, exception_on_overflow=False)
    recognition.send_audio_frame(data)
