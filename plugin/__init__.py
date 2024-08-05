from event import event_manager


def test(_):
    print('test1')



event_manager.subscribe('OnInitial', test)