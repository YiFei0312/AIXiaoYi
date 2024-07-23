import time
import dashscope
import sqlite3
import os
import functools


personalities = {}
personality = ''


def set_api_key():
    api_key = input("请输入您的api_key:")
    conn = sqlite3.connect('config.db')
    c = conn.cursor()
    c.execute('UPDATE Config SET dashscope_api_key = ? WHERE id = 1', (api_key,))
    conn.commit()
    dashscope.api_key = api_key
    c.close()
    conn.close()


def read_config():
    global personality
    global personalities
    conn = sqlite3.connect('config.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Personality')
    personalities_from_db = c.fetchall()
    for row in personalities_from_db:
        personalities[row[1]] = row[2]
    c.execute('SELECT * FROM Config')
    config_from_db = c.fetchall()
    dashscope.api_key = config_from_db[0][1]
    if config_from_db[0][1] == '':
        print('未找到api_key，请输入api_key')
        set_api_key()
    c.execute('SELECT * FROM Personality WHERE id = ?', (config_from_db[0][2],))
    personality_from_db = c.fetchall()
    personality = personality_from_db[0][2]
    c.close()
    conn.close()
    print('读取配置成功')


def retry_on_failure(max_retries=3, delay=2, exceptions=(Exception,)):
    # 重试 装饰器
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except exceptions as e:
                    if attempt < max_retries:
                        logger.error(
                            f"Function '{func.__name__}' failed on attempt {attempt + 1}: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"Function '{func.__name__}' failed after {max_retries} retries: {e}")
                        raise

        return wrapper

    return decorator


if __name__ != '__main__':
    # 获取config/__init__.py的绝对路径
    mypackage_init_path = os.path.abspath(__file__)
    mypackage_dir = os.path.dirname(mypackage_init_path)
    file_path = os.path.join(mypackage_dir, 'xiaoyi.log')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('')
