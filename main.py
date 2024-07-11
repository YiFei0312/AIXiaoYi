import os
import time
from speech import Speech_Recognition, Speech_Synthesizer, Speech_Waken
import qwen
from config import config
from logging import getLogger
import logging



logger = getLogger(__name__)


def safe_create_dir(directory):
    """安全创建目录"""
    try:
        if not os.path.exists(directory):
            os.mkdir(directory)
    except Exception as e:
        logger.error(f"创建目录失败: {directory}, 错误: {e}")


def main():
    config_dir = './config'
    config_file = './config/config.ini'

    # 安全创建配置文件目录
    safe_create_dir(config_dir)

    if not os.path.exists(config_file):
        try:
            logger.info("配置文件不存在，正在生成...")
            config.generate_config_file()
        except Exception as e:
            logger.error(f"生成配置文件失败: {config_file}, 错误: {e}")
            return

    try:
        logger.info("正在读取配置文件...")
        config.read_config_file()
    except Exception as e:
        logger.error(f"读取配置文件失败: {config_file}, 错误: {e}")
        return

    manager = qwen.BookkeepingManager()

    while True:
        try:
            Speech_Waken.speech_recognize_keyword_locally_from_microphone()
        except Exception as e:
            logger.error(f"启动语音唤醒失败: {e}")
            return
        try:
            Speech_Synthesizer.start('唉！我在！')
            Speech_Recognition.start()
            logger.info('等待语音输入中...')

            while True:
                if Speech_Recognition.start_time is not None and time.time() - Speech_Recognition.start_time > 30:
                    Speech_Recognition.stop()
                    Speech_Recognition.start()

                try:
                    Speech_Recognition.send_audio_frame()
                except Exception as e:
                    logger.error(f"发送音频帧失败: {e}")
                    break

                if Speech_Recognition.last_voice_time is not None and time.time() - Speech_Recognition.last_voice_time > 1:
                    logger.info(f"你说：{Speech_Recognition.latest_sentence}")
                    if Speech_Recognition.last_voice_time is not None:
                        Speech_Recognition.stop()
                    try:
                        Speech_Synthesizer.start(
                            manager.get_qwen_response_parallel(Speech_Recognition.latest_sentence))
                    except Exception as e:
                        logger.error(f"语音合成失败: {e}")
                    logger.info('对话结束，程序重新开始...')
                    break
        except Exception as e:
            logger.error(f"主循环异常: {e}")
            time.sleep(5)  # 休眠5秒后重新尝试，避免过多占用资源


if __name__ == "__main__":
    # 设置日志输出级别和格式
    logger.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    main()

