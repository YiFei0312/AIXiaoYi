import asyncio
import time
import vlc
import requests
import parsel
from prettytable import PrettyTable
from urllib.parse import quote


class MusicPlayer:
    done = False
    states = None

    def __init__(self):
        """
        初始化音乐播放器
        """
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, self.on_playing)
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_playback_ended)

    def on_playback_ended(self, event):
        """
        播放结束时的回调函数
        """

    def on_playing(self, event):
        """播放开始时的回调函数"""
        # print("音乐开始播放！")
        self.states = 'playing'
        self.done = True

    def play_music(self, url):
        """
        播放音乐
        :param url: 音乐地址
        :return:
        """
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.player.play()

    def pause_music(self):
        """
        暂停播放音乐
        """
        self.player.pause()

    def resume_music(self):
        """
        恢复播放音乐
        """
        self.player.play()

    def stop_music(self):
        """
        停止播放音乐
        """
        self.player.stop()

    def search_music(self, keyword):
        """
        搜索音乐
        :param keyword: 搜索关键词
        :return: play_url 播放地址
        """
        # 待转换的中文字符串
        chinese_string = keyword

        # 使用quote函数进行URL编码
        encoded_string = quote(chinese_string)
        link = f'https://www.gequbao.com/s/{encoded_string}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        }
        # 发送请求
        link_data = requests.get(url=link, headers=headers)
        # 获取响应文本数据
        html = link_data.text
        selector = parsel.Selector(html)
        rows = selector.css('.row')[1:2]
        tb = PrettyTable()
        # 添加字段名
        tb.field_names = ['序号', '歌名', '歌手']
        # 自定义变量
        page = 0
        song_list = []
        for row in rows:
            # 提取歌名
            SongName = row.css('a.text-primary::text').get().strip()
            # 提取ID
            SongId = row.css('a.text-primary::attr(href)').get().split('/')[-1]
            # 提取歌手
            Singer = row.css('.text-success::text').get().strip()
            # 创建一个字典来存储歌曲信息
            song_info = {'id': SongId, 'name': SongName, 'singer': Singer}
            # 将字典添加到列表中
            song_list.append(song_info)
            # 打印歌曲信息，可选
            print('歌曲id:', SongId)
            print('歌曲名:', SongName)
            print('歌手名:', Singer)
        first_song_id = song_list[0]['id'] if song_list else None
        # 请求网址
        url = f'https://www.gequbao.com/api/play_url?id={first_song_id}&json=1'
        # 发送请求
        response = requests.get(url=url, headers=headers)
        # 获取响应json数据
        json_data = response.json()
        # 提取歌曲链接
        play_url = json_data['data']['url']
        print('播放地址:', play_url)
        return play_url


music_player = MusicPlayer()


def play_music(description):
    message = ''
    try:
        music = music_player.search_music(description)
        if music:
            music_player.play_music(music)
            #while not music_player.done:
            #time.sleep(.1)
            #if music_player.states == 'playing':
            print(f"正在播放歌曲: {description}")
            message = f"正在播放歌曲: {description}"
            return message

        else:
            print("未找到对应歌曲")
            message = "未找到对应歌曲"
            return message
    except Exception as e:
        print(f"播放音乐时发生错误: {e}")
        message = "播放音乐时发生错误"
        return message


def pause_music():
    try:
        # 暂停播放，这里假设MusicPlayer的pause_music方法不需要额外参数
        print('暂停播放了喵！')
        music_player.pause_music()
    except Exception as e:
        print(f"暂停播放时发生错误: {e}")
    message = '暂停播放了喵！'
    return message


def resume_music():
    try:
        # 继续播放，这里假设MusicPlayer的pause_music方法不需要额外参数
        print('继续播放了喵！')
        music_player.resume_music()
    except Exception as e:
        print(f"继续播放时发生错误: {e}")
    message = '继续播放了喵！'
    return message


def stop_music():
    try:
        # 停止播放，这里假设MusicPlayer的pause_music方法不需要额外参数
        print('停止播放了喵！')
        music_player.stop_music()
    except Exception as e:
        print(f"停止播放时发生错误: {e}")
    message = '停止播放了喵！'
    return message


if __name__ == "__main__":
    song_name = input("请输入歌曲名:")
    player = MusicPlayer()
    player.play_music(player.search_music(song_name))
    print("播放中...")
    time.sleep(10)
    print("音乐播放已结束！")
