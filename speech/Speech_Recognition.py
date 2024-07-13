import pyaudio
from dashscope.audio.asr import (Recognition, RecognitionCallback,
                                 RecognitionResult)
import time

class Recognizer:
    def __init__(self):
        self.mic = None
        self.stream = None
        self.latest_sentence = ''
        self.display_text = ''
        self.max_chars = 40
        self.clear_flag = False
        self.last_voice_time = None
        self.start_time = None
        self.callback = self.Callback(self)  # 传递外部类实例
        self.recognition = Recognition(model='paraformer-realtime-v1',
                                       format='pcm',
                                       sample_rate=16000,
                                       callback=self.callback)

    class Callback(RecognitionCallback):
        def __init__(self, parent):
            super().__init__()
            self.parent = parent  # 保存外部类实例的引用

        def on_open(self):
            self.parent.mic = pyaudio.PyAudio()
            self.parent.stream = self.parent.mic.open(format=pyaudio.paInt16,
                                                      channels=1,
                                                      rate=16000,
                                                      input=True)
            self.parent.start_time = time.time()

        def on_close(self):
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

    def stop(self):
        self.recognition.stop()

    def send_audio_frame(self):
        if self.stream:
            data = self.stream.read(3200, exception_on_overflow=False)
            self.recognition.send_audio_frame(data)
