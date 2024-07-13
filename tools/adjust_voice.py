from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import ctypes


def adjust_volume(percent_change):
    # 获取当前的音频设备
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # 获取当前音量（0.0 到 1.0）
    current_volume = volume.GetMasterVolumeLevelScalar()

    # 调整音量百分比
    new_volume = current_volume + percent_change / 100

    # 限制音量在有效范围内
    new_volume = max(0.0, min(1.0, new_volume))

    # 设置新的音量
    volume.SetMasterVolumeLevelScalar(new_volume, None)

    # 输出当前音量和新音量
    print(f"Current Volume: {current_volume * 100:.2f}%")
    print(f"New Volume: {new_volume * 100:.2f}%")

def set_volume(volume_level):
    """
    设置音量到指定的百分比。
    参数:
        volume_level (float): 音量百分比，范围是0到100。
    """
    # 获取当前的音频设备
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_controller = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))

    # 将音量百分比转换为0.0到1.0的范围
    normalized_volume = volume_level / 100

    # 设置新的音量
    volume_controller.SetMasterVolumeLevelScalar(normalized_volume, None)

    # 输出新音量
    print(f"New Volume: {volume_level:.2f}%")




