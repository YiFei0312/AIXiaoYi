import datetime


def get_current_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"当前时间是: {current_time}喵！")
    return current_time