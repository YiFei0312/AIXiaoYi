from .EventManager import *


class CheckModelFileEvent(Event):
    pass


class ReadConfigEvent(Event):
    pass


class WeakUpEvent(Event):
    pass

class SpeechRecognizeEvent(Event):
    pass

class GetResponseEvent(Event):
    def __init__(self, data):
        super().__init__(data)

class SpeechSynthesizerEvent(Event):
    def __init__(self, data):
        super().__init__(data)

# class ProgramStateController:
#     """程序状态控制器类"""
#
#     def __init__(self):
#         self._state = 'initial'
#         self._state_transitions = {
#             'initial': {'next': 'loading', 'handler': self._handle_initial},
#             'loading': {'next': 'ready', 'handler': self._handle_loading},
#             'ready': {'next': 'listening', 'handler': self._handle_ready},
#             'listening': {'next': 'processing', 'handler': self._handle_listening},
#             'processing': {'next': 'speaking', 'handler': self._handle_processing},
#             'speaking': {'next': 'ready', 'handler': self._handle_speaking},
#         }
#         self._state_history = []
#
#     # def handle_event(self, event):
#     #     """处理事件"""
#     #     if isinstance(event, tuple(self._state_transitions[self._state]['events'])):
#     #         self.change_state()
#
#     def set_state(self, new_state):
#         """设置当前状态"""
#         if new_state in self._state_transitions:
#             self._state = new_state
#             self._state_history.append(new_state)
#             self._state_transitions[new_state]['handler']()
#         else:
#             raise ValueError(f"Invalid state: {new_state}")
#
#     def change_state(self):
#         """改变当前状态"""
#         next_state = self._state_transitions[self._state]['next']
#         self._state_history.append(self._state)
#         self._state = next_state
#         self._state_transitions[next_state]['handler']()
#
#     def current_state(self):
#         """返回当前状态"""
#         return self._state
#
#     def state_history(self):
#         """返回状态历史记录"""
#         return self._state_history
#
#     def _handle_initial(self):
#         """处理初始状态"""
#         print("进入初始状态")
#
#     def _handle_loading(self):
#         """处理加载状态"""
#         print("进入加载状态")
#
#     def _handle_ready(self):
#         """处理就绪状态"""
#         print("进入就绪状态")
#
#     def _handle_listening(self):
#         """处理监听状态"""
#         print("进入监听状态")
#
#     def _handle_processing(self):
#         """处理处理状态"""
#         print("进入处理状态")
#
#     def _handle_speaking(self):
#         """处理说话状态"""
#         print("进入说话状态")
