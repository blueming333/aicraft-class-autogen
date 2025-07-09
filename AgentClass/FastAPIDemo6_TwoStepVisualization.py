# DeepSeek 两步可视化演示脚本
# 专门演示：第一次调用获取数据，第二次调用绘制图表
# 简洁版本，专注于两步过程的演示

import json
import os
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 设置matplotlib中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (10, 6)

load_dotenv()

@dataclass
class DeepSeekConfig:
    """DeepSeek 配置类"""
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 4000
    temperature: float = 0.1

class DataTools:
    """数据获取工具类"""
    
    @staticmethod
    def generate_random_numbers(count: int = 10, min_val: float = 0, max_val: float = 100) -> Dict:
        """生成随机数字"""
        numbers = [round(random.uniform(min_val, max_val), 2) for _ in range(count)]
        return {
            "numbers": numbers,
            "count": count,
            "range": {"min": min(numbers), "max": max(numbers)},
            "mean": round(sum(numbers) / len(numbers), 2)
        }
    
    @staticmethod
    def generate_sales_data(quarters: List[str], products_per_quarter: int = 4) -> Dict:
        """生成销售数据"""
        sales_data = {}
        for quarter in quarters:
            sales_data[quarter] = [round(random.uniform(50, 200), 2) for _ in range(products_per_quarter)]
        
        return {
            "sales_data": sales_data,
            "quarters": quarters,
            "total_quarters": len(quarters)
        }

class PlotTools:
    """绘图工具类"""
    
    @staticmethod
    def create_bar_chart(data: List[float], title: str = "柱状图", labels: List[str] = None) -> Dict:
        """创建柱状图"""
        try:
            plt.figure(figsize=(10, 6))
            
            if labels and len(labels) == len(data):
                x_labels = labels
            else:
                x_labels = [f"项目{i+1}" for i in range(len(data))]
            
            bars = plt.bar(x_labels, data, color='skyblue', alpha=0.8)
            plt.title(title)
            plt.xlabel("项目")
            plt.ylabel("数值")
            
            # 显示数值
            for bar, value in zip(bars, data):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(data)*0.01, 
                        f'{value:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.show()
            
            return {
                "chart_type": "柱状图",
                "title": title,
                "data_count": len(data),
                "status": "图表已生成并显示"
            }
        except Exception as e:
            return {"error": f"柱状图生成错误: {e}"}
    
    @staticmethod
    def create_line_chart(data: List[float], title: str = "折线图", labels: List[str] = None) -> Dict:
        """创建折线图"""
        try:
            plt.figure(figsize=(10, 6))
            
            if labels and len(labels) == len(data):
                x_values = labels
                plt.plot(x_values, data, marker='o', linewidth=2, markersize=6)
            else:
                x_values = list(range(1, len(data) + 1))
                plt.plot(x_values, data, marker='o', linewidth=2, markersize=6)
            
            plt.title(title)
            plt.xlabel("数据点")
            plt.ylabel("数值")
            plt.grid(True, alpha=0.3)
            
            # 标注数值
            for i, value in enumerate(data):
                if labels:
                    plt.annotate(f'{value:.1f}', (labels[i], value), textcoords="offset points", 
                               xytext=(0,10), ha='center')
                else:
                    plt.annotate(f'{value:.1f}', (i+1, value), textcoords="offset points", 
                               xytext=(0,10), ha='center')
            
            plt.tight_layout()
            plt.show()
            
            return {
                "chart_type": "折线图",
                "title": title,
                "data_count": len(data),
                "status": "图表已生成并显示"
            }
        except Exception as e:
            return {"error": f"折线图生成错误: {e}"}
    
    @staticmethod
    def create_comparison_chart(datasets: Dict[str, List[float]], title: str = "对比图") -> Dict:
        """创建对比图表"""
        try:
            plt.figure(figsize=(12, 8))
            
            quarters = list(datasets.keys())
            data_values = list(datasets.values())
            
            x_pos = np.arange(len(data_values[0]))
            bar_width = 0.8 / len(quarters)
            colors = ['skyblue', 'lightcoral', 'lightgreen', 'gold']
            
            for i, (quarter, values) in enumerate(datasets.items()):
                offset = (i - len(quarters)/2 + 0.5) * bar_width
                plt.bar(x_pos + offset, values, bar_width, 
                       label=quarter, color=colors[i % len(colors)], alpha=0.8)
            
            plt.xlabel('产品')
            plt.ylabel('销量')
            plt.title(title)
            plt.xticks(x_pos, [f'产品{i+1}' for i in range(len(data_values[0]))])
            plt.legend()
            
            plt.tight_layout()
            plt.show()
            
            return {
                "chart_type": "对比柱状图",
                "title": title,
                "datasets_count": len(datasets),
                "status": "对比图表已生成并显示"
            }
        except Exception as e:
            return {"error": f"对比图表生成错误: {e}"}

class TwoStepDemo:
    """两步演示类"""
    
    def __init__(self, config: DeepSeekConfig):
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.config = config
        self.data_tools = DataTools()
        self.plot_tools = PlotTools()
        
        # 数据获取工具定义
        self.data_tools_def = [
            {
                "type": "function",
                "function": {
                    "name": "generate_random_numbers",
                    "description": "生成指定数量的随机数字",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer", "description": "生成数字的数量"},
                            "min_val": {"type": "number", "description": "最小值", "default": 0},
                            "max_val": {"type": "number", "description": "最大值", "default": 100}
                        },
                        "required": ["count"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_sales_data",
                    "description": "生成销售数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "quarters": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "季度列表"
                            },
                            "products_per_quarter": {
                                "type": "integer",
                                "description": "每季度产品数量",
                                "default": 4
                            }
                        },
                        "required": ["quarters"]
                    }
                }
            }
        ]
        
        # 绘图工具定义
        self.plot_tools_def = [
            {
                "type": "function",
                "function": {
                    "name": "create_bar_chart",
                    "description": "创建柱状图",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "数据列表"
                            },
                            "title": {"type": "string", "description": "图表标题"},
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "标签列表"
                            }
                        },
                        "required": ["data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_line_chart",
                    "description": "创建折线图",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "数据列表"
                            },
                            "title": {"type": "string", "description": "图表标题"},
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "标签列表"
                            }
                        },
                        "required": ["data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_comparison_chart",
                    "description": "创建对比图表",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "datasets": {
                                "type": "object",
                                "description": "数据集字典，键为类别名，值为数据列表"
                            },
                            "title": {"type": "string", "description": "图表标题"}
                        },
                        "required": ["datasets"]
                    }
                }
            }
        ]
    
    def call_data_function(self, function_name: str, arguments: Dict) -> Any:
        """执行数据获取函数"""
        function_map = {
            "generate_random_numbers": self.data_tools.generate_random_numbers,
            "generate_sales_data": self.data_tools.generate_sales_data
        }
        
        if function_name in function_map:
            try:
                return function_map[function_name](**arguments)
            except Exception as e:
                return {"error": f"数据函数执行错误: {e}"}
        else:
            return {"error": f"未知数据函数: {function_name}"}
    
    def call_plot_function(self, function_name: str, arguments: Dict) -> Any:
        """执行绘图函数"""
        function_map = {
            "create_bar_chart": self.plot_tools.create_bar_chart,
            "create_line_chart": self.plot_tools.create_line_chart,
            "create_comparison_chart": self.plot_tools.create_comparison_chart
        }
        
        if function_name in function_map:
            try:
                return function_map[function_name](**arguments)
            except Exception as e:
                return {"error": f"绘图函数执行错误: {e}"}
        else:
            return {"error": f"未知绘图函数: {function_name}"}
    
    def step1_get_data(self, user_request: str) -> tuple:
        """第一步：获取数据"""
        print("🔄 第一步：调用AI获取数据...")
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是数据生成助手。根据用户需求，选择合适的数据生成工具。只生成数据，不进行绘图。"
                },
                {"role": "user", "content": user_request}
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=self.data_tools_def,
                tool_choice="auto",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                # 执行数据获取函数
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"🔧 调用数据工具: {function_name}")
                print(f"📋 参数: {arguments}")
                
                result = self.call_data_function(function_name, arguments)
                print(f"✅ 数据获取完成: {result}")
                
                return result, function_name
            else:
                return {"error": "AI未调用数据工具"}, None
                
        except Exception as e:
            return {"error": f"第一步执行错误: {e}"}, None
    
    def step2_create_plot(self, data_result: Dict, plot_request: str) -> str:
        """第二步：创建图表"""
        print("\n🎨 第二步：调用AI创建图表...")
        
        try:
            # 将数据结果转换为可用的上下文
            data_context = f"已获取到数据：{json.dumps(data_result, ensure_ascii=False)}"
            
            messages = [
                {
                    "role": "system",
                    "content": "你是图表绘制助手。根据提供的数据和用户需求，选择合适的绘图工具创建图表。"
                },
                {"role": "user", "content": f"{data_context}\n\n{plot_request}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=self.plot_tools_def,
                tool_choice="auto",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                # 执行绘图函数
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"🔧 调用绘图工具: {function_name}")
                print(f"📋 参数: {arguments}")
                
                result = self.call_plot_function(function_name, arguments)
                print(f"✅ 图表绘制完成: {result}")
                
                return f"图表绘制成功：{result.get('status', '已完成')}"
            else:
                return "AI未调用绘图工具，可能需要调整请求"
                
        except Exception as e:
            return f"第二步执行错误: {e}"
    
    def run_two_step_demo(self, scenario: Dict):
        """运行两步演示"""
        print(f"\n{'='*60}")
        print(f"📊 演示场景: {scenario['title']}")
        print(f"📝 任务描述: {scenario['description']}")
        print(f"{'='*60}")
        
        # 第一步：获取数据
        data_result, data_function = self.step1_get_data(scenario['data_request'])
        
        if 'error' in data_result:
            print(f"❌ 第一步失败: {data_result['error']}")
            return
        
        # 第二步：创建图表
        plot_result = self.step2_create_plot(data_result, scenario['plot_request'])
        print(f"\n🎉 演示完成: {plot_result}")

def main():
    """主函数"""
    print("🎨 DeepSeek 两步可视化演示")
    print("=" * 50)
    print("💡 演示AI如何通过两次调用完成数据可视化：")
    print("   第一步：调用AI获取数据")
    print("   第二步：调用AI绘制图表")
    print("=" * 50)
    
    # 配置
    config = DeepSeekConfig(
        api_key=os.getenv('OPENAI_API_KEY', 'your-api-key-here'),
        base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
        model="gpt-4.1",
        temperature=0.1
    )
    
    if config.api_key == 'your-api-key-here':
        print("⚠️ 请先设置 OPENAI_API_KEY 环境变量")
        return
    
    demo = TwoStepDemo(config)
    
    # 演示场景
    scenarios = [
        {
            "title": "随机数据柱状图",
            "description": "生成随机数据，然后用柱状图展示",
            "data_request": "生成10个随机数字，范围在20到80之间",
            "plot_request": "用这些数据创建一个柱状图，标题为'随机数据分布'"
        },
        {
            "title": "销售数据趋势图",
            "description": "生成销售数据，然后用折线图展示趋势",
            "data_request": "生成第一季度、第二季度、第三季度的销售数据，每季度6个产品",
            "plot_request": "为每个季度的平均销量创建折线图，标题为'季度销售趋势'"
        },
        {
            "title": "多季度对比图",
            "description": "生成多季度数据，然后创建对比图表",
            "data_request": "生成春季、夏季、秋季三个季度的销售数据，每季度4个产品",
            "plot_request": "创建对比图表显示三个季度的销售数据对比，标题为'季度销售对比'"
        }
    ]
    
    # 运行演示
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🚀 开始第 {i} 个演示...")
        demo.run_two_step_demo(scenario)
        
        if i < len(scenarios):
            input("\n按回车键继续下一个演示...")
    
    print("\n" + "✅" * 20)
    print("🎉 所有演示完成！")
    print("💡 通过这个演示，你可以看到AI是如何:")
    print("   1. 智能理解数据需求并生成数据")
    print("   2. 根据数据特点选择合适的图表类型")
    print("   3. 调用相应的绘图工具完成可视化")
    print("✅" * 20)

if __name__ == "__main__":
    main() 