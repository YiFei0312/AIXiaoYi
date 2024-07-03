import pyaudio
from dashscope.audio.tts import ResultCallback, SpeechSynthesizer, SpeechSynthesisResult

class Callback(ResultCallback):
    _player = None
    _stream = None

    def on_open(self):
        # print('Speech synthesizer is opened.')
        self._player = pyaudio.PyAudio()
        self._stream = self._player.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=48000,
            output=True)

    # def on_complete(self):
    #     print('Speech synthesizer is completed.')
    #
    # def on_error(self, response: SpeechSynthesisResponse):
    #     print('Speech synthesizer failed, response is %s' % (str(response)))
    def on_close(self):
        # print('Speech synthesizer is closed.')
        self._stream.stop_stream()
        self._stream.close()
        self._player.terminate()

    def on_event(self, result: SpeechSynthesisResult):
        if result.get_audio_frame() is not None:
            # print('audio result length:', sys.getsizeof(result.get_audio_frame()))
            self._stream.write(result.get_audio_frame())

        # if result.get_timestamp() is not None:
        #     print('timestamp result:', str(result.get_timestamp()))

callback = Callback()
def start(text):
    SpeechSynthesizer.call(model='sambert-zhiwei-v1',
                           text=text,
                           sample_rate=48000,
                           format='pcm',
                           callback=callback)
