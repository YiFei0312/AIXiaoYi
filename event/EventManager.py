import threading
import queue


class Event:
    """事件基类"""

    def __init__(self, data=None):
        self.data = data


class EventManager:
    """事件管理器类"""

    def __init__(self):
        self._event_listeners = {}
        self._event_queue = queue.Queue()
        self._event_thread = threading.Thread(target=self._process_events)
        self._event_thread.start()

    def subscribe(self, event_type, callback):
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        if event_type in self._event_listeners:
            callbacks = self._event_listeners[event_type]
            try:
                callbacks.remove(callback)
            except ValueError:
                pass

    def unsubscribe_all(self, event_type=None):
        if event_type:
            if event_type in self._event_listeners:
                del self._event_listeners[event_type]
        else:
            self._event_listeners.clear()

    def post(self, event):
        self._event_queue.put(event)

    def _process_events(self):
        while True:
            event = self._event_queue.get()
            if event is None:
                break
            self._dispatch(event)
            self._event_queue.task_done()

    def _dispatch(self, event):
        event_type = type(event).__name__
        for callback in self._event_listeners.get(event_type, []):
            callback(event)

    def shutdown(self):
        self._event_queue.put(None)
        self._event_thread.join()


# 示例使用
if __name__ == "__main__":
    class MyEvent(Event):
        def __init__(self, data):
            super().__init__(data)


    def handle_event(event):
        print(f"Handling event with data: {event.data}")


    # 创建事件管理器实例
    event_manager = EventManager()

    # 订阅事件
    event_manager.subscribe('MyEvent', handle_event)

    # 发布事件
    event_manager.post(MyEvent("Hello, World!"))