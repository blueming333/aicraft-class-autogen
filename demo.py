# 帮我实现一个简单的冒泡算法

import math

def scientific_calculator():
    print("欢迎使用简单科学计算器！")
    print("可用操作：加法(+)、减法(-)、乘法(*)、除法(/)、幂(**)、开方(sqrt)、正弦(sin)、余弦(cos)、对数(log)")
    while True:
        op = input("请输入操作类型（+、-、*、/、**、sqrt、sin、cos、log），或输入exit退出：")
        if op == "exit":
            print("退出计算器。")
            break
        if op in ["+", "-", "*", "/", "**"]:
            try:
                a = float(input("请输入第一个数字："))
                b = float(input("请输入第二个数字："))
                if op == "+":
                    print("结果：", a + b)
                elif op == "-":
                    print("结果：", a - b)
                elif op == "*":
                    print("结果：", a * b)
                elif op == "/":
                    if b == 0:
                        print("错误：除数不能为0")
                    else:
                        print("结果：", a / b)
                elif op == "**":
                    print("结果：", a ** b)
            except ValueError:
                print("输入无效，请输入数字。")
        elif op in ["sqrt", "sin", "cos", "log"]:
            try:
                a = float(input("请输入数字："))
                if op == "sqrt":
                    if a < 0:
                        print("错误：不能对负数开方")
                    else:
                        print("结果：", math.sqrt(a))
                elif op == "sin":
                    print("结果：", math.sin(a))
                elif op == "cos":
                    print("结果：", math.cos(a))
                elif op == "log":
                    if a <= 0:
                        print("错误：对数的输入必须大于0")
                    else:
                        print("结果：", math.log(a))
            except ValueError:
                print("输入无效，请输入数字。")
        else:
            print("不支持的操作类型，请重新输入。")

# 示例：运行科学计算器
if __name__ == "__main__":
    scientific_calculator()

    # 增加 main 入口函数
    def main():
        scientific_calculator()

    # 如果作为主程序运行，则调用 main
    if __name__ == "__main__":
        main()


