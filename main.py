import config
import time
import qwen
import speech
from config import retry_on_failure
from logging import getLogger
import logging
from logging.handlers import TimedRotatingFileHandler
from concurrent.futures import ThreadPoolExecutor
from event import *
import plugin


logger = getLogger(__name__)
manager = qwen.BookkeepingManager()
speech_recognizer = speech.Recognizer()




class ProgramStateController:
    """程序状态控制器类"""

    def __init__(self):
        # self._state = 'initial'
        self.user_say = ''
        self.xiaoyi_say = ''
        self._state_transitions = {
            'initial': {'next': 'loading', 'handler': self._handle_initial},
            'loading': {'next': 'ready', 'handler': self._handle_loading},
            'ready': {'next': 'listening', 'handler': self._handle_ready},
            'listening': {'next': 'processing', 'handler': self._handle_listening},
            'processing': {'next': 'processing', 'handler': self._handle_processing},
            'replying': {'next': 'speaking', 'handler': self._handle_replying},
            'speaking': {'next': 'ready', 'handler': self._handle_speaking},
        }
        self._state_history = []

    # def handle_event(self, event):
    #     """处理事件"""
    #     if isinstance(event, tuple(self._state_transitions[self._state]['events'])):
    #         self.change_state()

    def set_state(self, new_state):
        """设置当前状态"""
        if new_state in self._state_transitions:
            self._state = new_state
            self._state_history.append(new_state)
            self._state_transitions[new_state]['handler']()
        else:
            raise ValueError(f"Invalid state: {new_state}")

    def change_state(self):
        """改变当前状态"""
        next_state = self._state_transitions[self._state]['next']
        self._state_history.append(self._state)
        self._state = next_state
        self._state_transitions[next_state]['handler']()

    def current_state(self):
        """返回当前状态"""
        return self._state

    def state_history(self):
        """返回状态历史记录"""
        return self._state_history

    def _handle_initial(self):
        """处理初始状态"""
        event_manager.post(OnInitial())
        try:
            print("正在检查模型文件...")
            speech.check_model_file()
            self.change_state()
        except Exception as e:
            logger.error(f"检查模型文件失败: {e}")

    def _handle_loading(self):
        """处理加载状态"""
        event_manager.post(OnLoading())
        try:
            print("正在读取配置...")
            logger.info("正在读取配置...")
            config.read_config()
            self.change_state()
        except Exception as e:
            logger.error(f"读取配置文件失败, 错误: {e}")
            raise

    def _handle_ready(self):
        """处理就绪状态"""
        event_manager.post(OnReady())
        try:
            speech.keyword_recognize()
            self.change_state()
        except Exception as e:
            logger.error(f"启动语音唤醒失败: {e}")
            raise
        print("进入就绪状态")

    def _handle_listening(self):
        """处理监听状态"""
        event_manager.post(OnListening())
        speech_recognizer.start()
        self.change_state()

    def _handle_processing(self):
        """处理处理状态"""
        event_manager.post(OnProcessing())
        if speech_recognizer.start_time is not None and time.time() - speech_recognizer.start_time > 30:
            speech_recognizer.stop()
            speech_recognizer.start()
        try:
            speech_recognizer.send_audio_frame()
        except Exception as e:
            logger.error(f"发送音频帧失败: {e}")

        if speech_recognizer.last_voice_time is not None and time.time() - speech_recognizer.last_voice_time > 1:
            logger.info(f"你说：{speech_recognizer.latest_sentence}")
            if speech_recognizer.last_voice_time is not None:
                speech_recognizer.stop()
            try:
                self.user_say = speech_recognizer.latest_sentence
                print(self.user_say)
                self.set_state('replying')
            except Exception as e:
                print(e)
                logger.error(f"识别语音失败: {e}")
        self.change_state()

    def _handle_replying(self):
        """处理回复状态"""
        event_manager.post(OnReplying(self.user_say))
        try:
            with ThreadPoolExecutor() as executor:
                try:
                    tool_response = executor.submit(manager.get_tool_response, self.user_say)
                except Exception as e:
                    logger.error(f"获取工具回复失败: {e}")
                try:
                    model_response = executor.submit(manager.get_response, self.user_say)
                except Exception as e:
                    logger.error(f"获取模型回复失败: {e}")
            if tool_response.result() is None:
                print(model_response.result())
                self.xiaoyi_say = model_response.result()
            else:
                manager.ai_bookkeeping = manager.ai_bookkeeping[:-1]
                manager.add_conversation(tool_response.result()[1], tool_response.result()[0])
                self.xiaoyi_say = tool_response.result()[0]
            # return controller.xiaoyi_say
            self.change_state()
        except Exception as e:
            logger.error(f"获取回复失败: {e}")

    def _handle_speaking(self):
        """处理说话状态"""
        event_manager.post(OnSpeaking(self.xiaoyi_say))
        speech.synthesizer(self.xiaoyi_say)


controller = ProgramStateController()


def main():
    controller.set_state('initial')


if __name__ == "__main__":
    # 设置日志输出级别和格式
    logger.setLevel(logging.ERROR)
    fh = TimedRotatingFileHandler('xiaoyi.log', when='midnight', interval=1, backupCount=30, encoding='utf-8')
    fh.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(console_handler)

    main()
