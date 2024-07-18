import dashscope
import sqlite3

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
