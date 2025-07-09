# DeepSeek Function Call 功能演示脚本
# 本脚本详细演示：
# 1. Function Call 基础概念与工具定义
# 2. 时间工具：获取当前时间、时区转换等
# 3. 数学工具：计算器、统计分析
# 4. 实用工具：天气查询、文本处理、数据转换
# 5. 复合场景：多工具协作完成复杂任务

import json
import os
import math
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv
# matplotlib相关导入已移除，专注于基础Function Call演示

load_dotenv()

# ====================================================================
# 1. Function Call 基础概念与工具定义
# ====================================================================

"""
DeepSeek Function Call 功能介绍：

核心功能：
- 让AI模型能够调用外部工具和函数
- 实现AI与现实世界的交互能力
- 支持多步骤推理和工具组合使用
- 提供结构化的工具调用和结果处理

主要应用场景：
1. 实时数据查询：天气、股价、新闻等
2. 计算工具：数学运算、数据分析、图表生成
3. 外部服务集成：API调用、数据库操作
4. 自动化任务：文件处理、邮件发送、报告生成
"""

@dataclass
class DeepSeekConfig:
    """DeepSeek 配置类"""
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 4000
    temperature: float = 0.1

class ToolBox:
    """工具箱类 - 包含各种实用工具函数"""
    
    # ====================================================================
    # 2. 时间工具
    # ====================================================================
    
    @staticmethod
    def get_current_time(timezone_name: str = "Asia/Shanghai") -> str:
        """
        获取当前时间
        
        Args:
            timezone_name: 时区名称，如 "Asia/Shanghai", "UTC", "America/New_York"
        
        Returns:
            格式化的当前时间字符串
        """
        timezone_map = {
            "UTC": timezone.utc,
            "Asia/Shanghai": timezone(timedelta(hours=8)),
            "America/New_York": timezone(timedelta(hours=-5)),
            "Europe/London": timezone(timedelta(hours=0)),
            "Asia/Tokyo": timezone(timedelta(hours=9))
        }
        
        tz = timezone_map.get(timezone_name, timezone(timedelta(hours=8)))
        current_time = datetime.now(tz)
        
        return {
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": timezone_name,
            "weekday": current_time.strftime("%A"),
            "timestamp": int(current_time.timestamp())
        }
    
    @staticmethod
    def calculate_time_difference(start_time: str, end_time: str) -> str:
        """
        计算时间差
        
        Args:
            start_time: 开始时间 (格式: YYYY-MM-DD HH:MM:SS)
            end_time: 结束时间 (格式: YYYY-MM-DD HH:MM:SS)
        
        Returns:
            时间差信息
        """
        try:
            start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            
            diff = end - start
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return {
                "time_difference": f"{days}天 {hours}小时 {minutes}分钟 {seconds}秒",
                "total_days": days,
                "total_hours": round(diff.total_seconds() / 3600, 2),
                "total_minutes": round(diff.total_seconds() / 60, 2)
            }
        except ValueError as e:
            return {"error": f"时间格式错误: {e}"}
    
    # ====================================================================
    # 3. 数学工具
    # ====================================================================
    
    @staticmethod
    def advanced_calculator(expression: str) -> str:
        """
        高级计算器
        
        Args:
            expression: 数学表达式，支持基础运算和数学函数
        
        Returns:
            计算结果
        """
        try:
            # 安全的数学表达式求值
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return {
                "expression": expression,
                "result": result,
                "result_type": type(result).__name__,
                "formatted_result": f"{result:,.6f}".rstrip('0').rstrip('.')
            }
        except Exception as e:
            return {"error": f"计算错误: {e}"}
    
    @staticmethod
    def generate_ascii_chart(data_points: List[float], chart_type: str = "bar") -> str:
        """
        生成ASCII字符图表
        
        Args:
            data_points: 数据点列表
            chart_type: 图表类型 ("bar", "line")
        
        Returns:
            ASCII图表字符串
        """
        if not data_points:
            return {"error": "数据点为空"}
        
        try:
            max_val = max(data_points)
            min_val = min(data_points)
            
            if chart_type == "bar":
                # ASCII柱状图
                chart_lines = []
                chart_lines.append(f"ASCII柱状图 (最大值: {max_val:.2f})")
                chart_lines.append("-" * 40)
                
                for i, value in enumerate(data_points):
                    normalized = int((value / max_val) * 20) if max_val > 0 else 0
                    bar = "█" * normalized
                    chart_lines.append(f"数据{i+1:2d}: {bar} {value:.2f}")
                
                return {
                    "chart_type": "ASCII柱状图",
                    "chart": "\n".join(chart_lines),
                    "data_summary": {
                        "count": len(data_points),
                        "max": max_val,
                        "min": min_val,
                        "avg": sum(data_points) / len(data_points)
                    }
                }
            
            elif chart_type == "line":
                # ASCII折线图
                chart_lines = []
                chart_lines.append(f"ASCII折线图 (范围: {min_val:.2f} - {max_val:.2f})")
                chart_lines.append("-" * 40)
                
                for i, value in enumerate(data_points):
                    normalized = int(((value - min_val) / (max_val - min_val)) * 20) if max_val > min_val else 10
                    line = " " * normalized + "●"
                    chart_lines.append(f"点{i+1:2d}: {line} {value:.2f}")
                
                return {
                    "chart_type": "ASCII折线图",
                    "chart": "\n".join(chart_lines),
                    "data_summary": {
                        "count": len(data_points),
                        "max": max_val,
                        "min": min_val,
                        "avg": sum(data_points) / len(data_points)
                    }
                }
                
        except Exception as e:
            return {"error": f"ASCII图表生成错误: {e}"}
    
    @staticmethod
    def statistical_analysis(numbers: List[float]) -> str:
        """
        统计分析
        
        Args:
            numbers: 数字列表
        
        Returns:
            统计分析结果
        """
        if not numbers:
            return {"error": "数据为空"}
        
        numbers.sort()
        n = len(numbers)
        
        # 基本统计
        mean = sum(numbers) / n
        median = numbers[n//2] if n % 2 == 1 else (numbers[n//2-1] + numbers[n//2]) / 2
        mode_count = {}
        for num in numbers:
            mode_count[num] = mode_count.get(num, 0) + 1
        mode = max(mode_count, key=mode_count.get)
        
        # 方差和标准差
        variance = sum((x - mean) ** 2 for x in numbers) / n
        std_dev = variance ** 0.5
        
        return {
            "count": n,
            "sum": sum(numbers),
            "mean": round(mean, 4),
            "median": median,
            "mode": mode,
            "range": numbers[-1] - numbers[0],
            "variance": round(variance, 4),
            "standard_deviation": round(std_dev, 4),
            "min": numbers[0],
            "max": numbers[-1],
            "quartile_1": numbers[n//4],
            "quartile_3": numbers[3*n//4]
        }
    
    # ====================================================================
    # 4. 实用工具
    # ====================================================================
    
    @staticmethod
    def mock_weather_query(city: str) -> str:
        """
        模拟天气查询
        
        Args:
            city: 城市名称
        
        Returns:
            天气信息
        """
        # 模拟天气数据
        weather_conditions = ["晴天", "多云", "阴天", "小雨", "大雨", "雪天"]
        temperatures = list(range(-10, 40))
        
        weather = {
            "city": city,
            "temperature": random.choice(temperatures),
            "condition": random.choice(weather_conditions),
            "humidity": random.randint(30, 90),
            "wind_speed": random.randint(0, 20),
            "air_quality": random.choice(["优", "良", "轻度污染", "中度污染"]),
            "forecast": [
                {
                    "date": f"明天",
                    "temperature": f"{random.randint(-5, 35)}°C",
                    "condition": random.choice(weather_conditions)
                },
                {
                    "date": f"后天", 
                    "temperature": f"{random.randint(-5, 35)}°C",
                    "condition": random.choice(weather_conditions)
                }
            ]
        }
        
        return weather
    
    @staticmethod
    def text_processor(text: str, operation: str) -> str:
        """
        文本处理工具
        
        Args:
            text: 输入文本
            operation: 操作类型 ("count", "reverse", "upper", "lower", "capitalize", "word_freq")
        
        Returns:
            处理结果
        """
        operations = {
            "count": lambda t: {
                "char_count": len(t),
                "word_count": len(t.split()),
                "line_count": len(t.split('\n')),
                "unique_chars": len(set(t.lower()))
            },
            "reverse": lambda t: t[::-1],
            "upper": lambda t: t.upper(),
            "lower": lambda t: t.lower(),
            "capitalize": lambda t: t.title(),
            "word_freq": lambda t: {
                word: t.lower().split().count(word) 
                for word in set(t.lower().split())
            }
        }
        
        if operation not in operations:
            return {"error": f"不支持的操作: {operation}"}
        
        try:
            result = operations[operation](text)
            return {
                "operation": operation,
                "original_text": text[:100] + "..." if len(text) > 100 else text,
                "result": result
            }
        except Exception as e:
            return {"error": f"处理错误: {e}"}
    
    @staticmethod
    def generate_random_data(data_type: str, count: int = 10) -> str:
        """
        生成随机数据
        
        Args:
            data_type: 数据类型 ("numbers", "names", "colors", "coordinates")
            count: 生成数量
        
        Returns:
            随机数据
        """
        generators = {
            "numbers": lambda: [round(random.uniform(0, 100), 2) for _ in range(count)],
            "names": lambda: [random.choice([
                "张三", "李四", "王五", "赵六", "孙七", "周八", "吴九", "郑十"
            ]) for _ in range(count)],
            "colors": lambda: [random.choice([
                "红色", "蓝色", "绿色", "黄色", "紫色", "橙色", "粉色", "黑色", "白色"
            ]) for _ in range(count)],
            "coordinates": lambda: [
                {"x": round(random.uniform(-180, 180), 4), 
                 "y": round(random.uniform(-90, 90), 4)} 
                for _ in range(count)
            ]
        }
        
        if data_type not in generators:
            return {"error": f"不支持的数据类型: {data_type}"}
        
        return {
            "data_type": data_type,
            "count": count,
            "data": generators[data_type]()
        }
    


class DeepSeekFunctionDemo:
    """DeepSeek Function Call 演示类"""
    
    def __init__(self, config: DeepSeekConfig):
        """初始化客户端和工具定义"""
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.config = config
        self.toolbox = ToolBox()
        
        # 定义可用工具
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "获取指定时区的当前时间",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "timezone_name": {
                                "type": "string",
                                "description": "时区名称，如 Asia/Shanghai, UTC, America/New_York",
                                "default": "Asia/Shanghai"
                            }
                        }
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "calculate_time_difference",
                    "description": "计算两个时间之间的差值",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_time": {
                                "type": "string",
                                "description": "开始时间，格式: YYYY-MM-DD HH:MM:SS"
                            },
                            "end_time": {
                                "type": "string", 
                                "description": "结束时间，格式: YYYY-MM-DD HH:MM:SS"
                            }
                        },
                        "required": ["start_time", "end_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "advanced_calculator",
                    "description": "执行数学计算，支持基础运算和数学函数",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "数学表达式，如 '2+3*4', 'sin(pi/2)', 'sqrt(16)'"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_ascii_chart",
                    "description": "生成ASCII字符图表",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_points": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "数据点列表"
                            },
                            "chart_type": {
                                "type": "string",
                                "enum": ["bar", "line"],
                                "description": "图表类型：柱状图、折线图"
                            }
                        },
                        "required": ["data_points"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "statistical_analysis",
                    "description": "对数字列表进行统计分析",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "numbers": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "要分析的数字列表"
                            }
                        },
                        "required": ["numbers"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mock_weather_query",
                    "description": "查询指定城市的天气信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称"
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "text_processor",
                    "description": "处理文本，支持多种操作",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "要处理的文本"
                            },
                            "operation": {
                                "type": "string",
                                "enum": ["count", "reverse", "upper", "lower", "capitalize", "word_freq"],
                                "description": "处理操作类型"
                            }
                        },
                        "required": ["text", "operation"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_random_data",
                    "description": "生成指定类型的随机数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_type": {
                                "type": "string",
                                "enum": ["numbers", "names", "colors", "coordinates"],
                                "description": "数据类型"
                            },
                            "count": {
                                "type": "integer",
                                "description": "生成数量",
                                "default": 10
                            }
                        },
                        "required": ["data_type"]
                    }
                }
            },

        ]
    
    def call_function(self, function_name: str, arguments: Dict) -> Any:
        """执行函数调用"""
        function_map = {
            "get_current_time": self.toolbox.get_current_time,
            "calculate_time_difference": self.toolbox.calculate_time_difference,
            "advanced_calculator": self.toolbox.advanced_calculator,
            "generate_ascii_chart": self.toolbox.generate_ascii_chart,
            "statistical_analysis": self.toolbox.statistical_analysis,
            "mock_weather_query": self.toolbox.mock_weather_query,
            "text_processor": self.toolbox.text_processor,
            "generate_random_data": self.toolbox.generate_random_data
        }
        
        if function_name in function_map:
            try:
                return function_map[function_name](**arguments)
            except Exception as e:
                return {"error": f"函数执行错误: {e}"}
        else:
            return {"error": f"未知函数: {function_name}"}
    
    def chat_with_tools(self, user_message: str) -> str:
        """与AI对话并支持工具调用"""
        try:
            messages = [
                {
                    "role": "system", 
                    "content": "你是一个智能助手，可以使用各种工具来帮助用户。当需要执行计算、获取时间、处理文本等任务时，请使用相应的工具函数。"
                },
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            message = response.choices[0].message
            
            # 处理工具调用
            if message.tool_calls:
                messages.append(message)
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 调用工具: {function_name}")
                    print(f"📋 参数: {arguments}")
                    
                    # 执行函数
                    result = self.call_function(function_name, arguments)
                    
                    # 添加工具结果到消息
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result, ensure_ascii=False),
                        "tool_call_id": tool_call.id
                    })
                
                # 获取最终回复
                final_response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
                
                return final_response.choices[0].message.content
            else:
                return message.content
                
        except Exception as e:
            return f"对话错误: {e}"

# ====================================================================
# 演示场景
# ====================================================================

def demo_basic_scenarios():
    """演示基础功能场景"""
    
    # 配置
    config = DeepSeekConfig(
        api_key=os.getenv('OPENAI_API_KEY', 'your-api-key-here'),
        base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
        model="gpt-4.1-mini",
        temperature=0.1
    )
    
    if config.api_key == 'your-api-key-here':
        print("⚠️ 请先设置 OPENAI_API_KEY 环境变量")
        return
    
    demo = DeepSeekFunctionDemo(config)
    
    print("🚀 DeepSeek Function Call 基础功能演示")
    print("=" * 80)
    
    # 基础功能演示场景
    basic_scenarios = [
        "现在北京时间几点？顺便告诉我纽约现在是几点",
        "帮我计算 sin(pi/4) + cos(pi/6) 的结果",
        "查询一下上海的天气情况",
        "帮我分析这段文字的词频：'人工智能正在改变世界，人工智能让生活更美好，智能助手帮助人们提高效率'",
        "计算从2024-01-01 09:00:00到2024-12-31 18:00:00有多长时间",
        "生成10个随机数字，然后用ASCII柱状图显示它们"
    ]
    
    for i, scenario in enumerate(basic_scenarios, 1):
        print(f"\n📌 基础场景 {i}: {scenario}")
        print("-" * 60)
        
        response = demo.chat_with_tools(scenario)
        print(f"🤖 AI回复:\n{response}")
        
        if i < len(basic_scenarios):
            print("\n" + "="*60)



def main():
    """主函数"""
    print("🚀 DeepSeek Function Call 基础功能演示")
    print("=" * 60)
    print("🔧 支持的工具：时间查询、数学计算、ASCII图表、天气查询、文本处理等")
    print("💡 演示AI如何智能地选择和组合使用不同工具来完成任务")
    print("=" * 60)
    
    demo_basic_scenarios()
    
    print("\n" + "✅" * 20)
    print("🎉 演示完成！")
    print("💻 要运行此演示，请确保：")
    print("   1. 安装依赖：pip install python-dotenv openai")
    print("   2. 设置环境变量：export OPENAI_API_KEY='your-api-key'")
    print("   3. (可选) 设置自定义API：export OPENAI_BASE_URL='your-api-base-url'")
    print("   4. 运行脚本：python FastAPIDemo5_DeepSeekFunctionCall.py")
    print("✅" * 20)

if __name__ == "__main__":
    main() 