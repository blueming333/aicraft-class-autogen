# Python 基础语法示例脚本
# 本脚本详细演示：
# 1. 变量与数据类型
# 2. 基本控制结构（if、for、while）
# 3. 函数定义与调用
# 4. 模块与包的导入

# 1. 变量与数据类型
# Python 是动态类型语言，变量无需声明类型，赋值即创建
int_var = 10                # 整型（int）
float_var = 3.14            # 浮点型（float）
str_var = "Hello, Python!"   # 字符串（str）
list_var = [1, 2, 3, 4]     # 列表（list）
dict_var = {"a": 1, "b": 2} # 字典（dict）

print("变量与数据类型示例：")
print(f"int_var: {int_var}, 类型: {type(int_var)}")
print(f"float_var: {float_var}, 类型: {type(float_var)}")
print(f"str_var: {str_var}, 类型: {type(str_var)}")
print(f"list_var: {list_var}, 类型: {type(list_var)}")
print(f"dict_var: {dict_var}, 类型: {type(dict_var)}")
print("-")

# 2. 基本控制结构
# if 语句
x = 5
if x > 0:
    print(f"if语句：x={x} 是正数")
else:
    print(f"if语句：x={x} 不是正数")

# for 循环
print("for循环遍历列表：")
for item in list_var:
    print(f"item: {item}")

# while 循环
print("while循环示例：")
count = 0
while count < 3:
    print(f"count: {count}")
    count += 1
print("-")

# 3. 函数定义与调用
def add(a, b):
    """
    这是一个简单的加法函数。
    参数：
        a: 第一个加数
        b: 第二个加数
    返回：
        两数之和
    """
    return a + b

result = add(3, 7)
print(f"函数调用示例：add(3, 7) = {result}")
print("-")

# 4. 模块与包的导入
# Python 标准库有很多内置模块，可以直接导入使用
import math  # 导入math模块
from datetime import datetime  # 从datetime模块导入datetime类

print(f"math.pi = {math.pi}")
print(f"当前时间: {datetime.now()}")

# 也可以导入自定义模块（如同目录下的其他.py文件）
# 例如：from mymodule import myfunc
# 这里只做演示，实际需有对应的mymodule.py文件 