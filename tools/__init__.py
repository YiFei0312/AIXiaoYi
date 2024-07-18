import os
import importlib
import sqlite3

# 创建一个字典来存储导入的函数
function_registry = {}

# 获取当前文件所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取目录中所有的.py文件，但排除__init__.py
modules = [f[:-3] for f in os.listdir(current_dir) if f.endswith('.py') and f != '__init__.py']

# 动态导入所有模块，并将其中的方法添加到function_registry字典中
for module_name in modules:
    module = importlib.import_module('.' + module_name, package=__package__)

    # 获取模块中所有的方法
    methods = [getattr(module, m) for m in dir(module) if callable(getattr(module, m))]

    # 将方法添加到function_registry字典中
    for method in methods:
        function_registry[method.__name__] = method

conn = sqlite3.connect('config.db')
c = conn.cursor()
c.execute('SELECT * FROM tools')
tools_from_db = c.fetchall()
tools = []
for row in tools_from_db:
    c.execute(f'SELECT * FROM parameters WHERE tool_id = {row[0]}')
    properties_list = c.fetchall()
    properties = []
    required_properties = []
    for property in properties_list:
        properties.append({
            property[2]: {
                "type": property[3],
                "description": property[4]
            }
        })
        required_properties.append(property[2])
    tool = {
        "type": row[3],
        "function": {
            "name": row[1],
            "description": row[2],
            "parameters": {
                'type': "object",
                'properties': properties,
            },
            "required": required_properties
        }
    }
    tools.append(tool)

c.execute('SELECT * FROM tools')
tools_from_db = c.fetchall()
TOOL_MAP = {}
for row in tools_from_db:
    tool_name = row[1]
    # 直接使用工具名称作为函数名称
    function = function_registry.get(tool_name)
    if function is not None:
        TOOL_MAP[tool_name] = function

c.close()
conn.close()