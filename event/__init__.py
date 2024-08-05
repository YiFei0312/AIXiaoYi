from .EventManager import *
event_manager = EventManager()


class OnInitial(Event):
    pass


class OnLoading(Event):
    pass


class OnReady(Event):
    pass


class OnListening(Event):
    pass


class OnProcessing(Event):
    pass


class OnReplying(Event):
    def __init__(self, data):
        super().__init__(data)


class OnSpeaking(Event):
    def __init__(self, data):
        super().__init__(data)
