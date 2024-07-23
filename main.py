import time
import speech
import qwen
import config
from config import retry_on_failure
from logging import getLogger
import logging
from logging.handlers import TimedRotatingFileHandler



logger = getLogger(__name__)


@retry_on_failure(max_retries=3, delay=5)
def main():
    """检查模型文件"""
    try:
        speech.cheak_modelfile()
    except Exception as e:
        logger.error(f"检查模型文件失败: {e}")
        raise
    """读取配置"""
    try:
        logger.info("正在读取配置...")
        config.read_config()
    except Exception as e:
        logger.error(f"读取配置文件失败, 错误: {e}")
        raise

    manager = qwen.BookkeepingManager()
    speech_recognizer = speech.Recognizer()

    while True:
        try:
            speech.keyword_recognize()
        except Exception as e:
            logger.error(f"启动语音唤醒失败: {e}")
            raise
        try:
            speech_recognizer.start()
            speech.synthesizer('唉！我在！')
            logger.info('等待语音输入中...')

            while True:
                if speech_recognizer.start_time is not None and time.time() - speech_recognizer.start_time > 30:
                    speech_recognizer.stop()
                    speech_recognizer.start()

                try:
                    speech_recognizer.send_audio_frame()
                except Exception as e:
                    logger.error(f"发送音频帧失败: {e}")
                    break

                if speech_recognizer.last_voice_time is not None and time.time() - speech_recognizer.last_voice_time > 1:
                    logger.info(f"你说：{speech_recognizer.latest_sentence}")
                    if speech_recognizer.last_voice_time is not None:
                        speech_recognizer.stop()
                    try:
                        speech.synthesizer(manager.get_qwen_response_parallel(speech_recognizer.latest_sentence))
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
    fh=TimedRotatingFileHandler('xiaoyi.log', when='midnight',interval=1,backupCount=30,encoding='utf-8')
    fh.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(console_handler)

    main()

