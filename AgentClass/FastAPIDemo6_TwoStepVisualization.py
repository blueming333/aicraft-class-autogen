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
    def create_bar_chart(data: List[float], title: str = "Bar Chart", labels: List[str] = None) -> Dict:
        """创建柱状图"""
        try:
            plt.figure(figsize=(10, 6))
            
            if labels and len(labels) == len(data):
                x_labels = labels
            else:
                x_labels = [f"Item{i+1}" for i in range(len(data))]
            
            bars = plt.bar(x_labels, data, color='skyblue', alpha=0.8)
            plt.title(title)
            plt.xlabel("Items")
            plt.ylabel("Values")
            
            # 显示数值
            for bar, value in zip(bars, data):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(data)*0.01, 
                        f'{value:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.show()
            
            return {
                "chart_type": "Bar Chart",
                "title": title,
                "data_count": len(data),
                "status": "Chart generated and displayed"
            }
        except Exception as e:
            return {"error": f"Bar chart generation error: {e}"}
    
    @staticmethod
    def create_line_chart(data: List[float], title: str = "Line Chart", labels: List[str] = None) -> Dict:
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
            plt.xlabel("Data Points")
            plt.ylabel("Values")
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
                "chart_type": "Line Chart",
                "title": title,
                "data_count": len(data),
                "status": "Chart generated and displayed"
            }
        except Exception as e:
            return {"error": f"Line chart generation error: {e}"}
    
    @staticmethod
    def create_comparison_chart(datasets: Dict[str, List[float]], title: str = "Comparison Chart") -> Dict:
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
            
            plt.xlabel('Products')
            plt.ylabel('Sales')
            plt.title(title)
            plt.xticks(x_pos, [f'Product{i+1}' for i in range(len(data_values[0]))])
            plt.legend()
            
            plt.tight_layout()
            plt.show()
            
            return {
                "chart_type": "Comparison Bar Chart",
                "title": title,
                "datasets_count": len(datasets),
                "status": "Comparison chart generated and displayed"
            }
        except Exception as e:
            return {"error": f"Comparison chart generation error: {e}"}

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
                    "description": "Generate specified number of random numbers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer", "description": "Number of random numbers to generate"},
                            "min_val": {"type": "number", "description": "Minimum value", "default": 0},
                            "max_val": {"type": "number", "description": "Maximum value", "default": 100}
                        },
                        "required": ["count"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_sales_data",
                    "description": "Generate sales data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "quarters": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of quarters"
                            },
                            "products_per_quarter": {
                                "type": "integer",
                                "description": "Number of products per quarter",
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
                    "description": "Create bar chart",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Data list"
                            },
                            "title": {"type": "string", "description": "Chart title"},
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Label list"
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
                    "description": "Create line chart",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Data list"
                            },
                            "title": {"type": "string", "description": "Chart title"},
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Label list"
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
                    "description": "Create comparison chart",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "datasets": {
                                "type": "object",
                                "description": "Dataset dictionary with category names as keys and data lists as values"
                            },
                            "title": {"type": "string", "description": "Chart title"}
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
                return {"error": f"Data function execution error: {e}"}
        else:
            return {"error": f"Unknown data function: {function_name}"}
    
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
                return {"error": f"Plot function execution error: {e}"}
        else:
            return {"error": f"Unknown plot function: {function_name}"}
    
    def step1_get_data(self, user_request: str) -> tuple:
        """第一步：获取数据"""
        print("🔄 第一步：调用AI获取数据...")
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a data generation assistant. Based on user requirements, select appropriate data generation tools. Only generate data, do not create charts."
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
                return {"error": "AI did not call data tools"}, None
                
        except Exception as e:
            return {"error": f"Step 1 execution error: {e}"}, None
    
    def step2_create_plot(self, data_result: Dict, plot_request: str) -> str:
        """第二步：创建图表"""
        print("\n🎨 第二步：调用AI创建图表...")
        
        try:
            # 将数据结果转换为可用的上下文
            data_context = f"Data obtained: {json.dumps(data_result, ensure_ascii=False)}"
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a chart drawing assistant. Based on the provided data and user requirements, select appropriate drawing tools to create charts."
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
                
                return f"Chart drawing successful: {result.get('status', 'Completed')}"
            else:
                return "AI did not call drawing tools, may need to adjust request"
                
        except Exception as e:
            return f"Step 2 execution error: {e}"
    
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
    # config = DeepSeekConfig(
    #     api_key=os.getenv('TONGYI_API_KEY', 'your-api-key-here'),
    #     base_url=os.getenv('TONGYI_BASE_URL', 'https://api.openai.com/v1'),
    #     model="qwen-plus",
    #     temperature=0.1
    # )

    config = DeepSeekConfig(
        api_key=os.getenv('DEEPSEEK_API_KEY', 'your-api-key-here'),
        base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.openai.com/v1'),
        model="deepseek-chat",
        temperature=0.1
    )
    
    if config.api_key == 'your-api-key-here':
        print("⚠️ 请先设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    demo = TwoStepDemo(config)
    
    # 演示场景
    scenarios = [
        {
            "title": "随机数据柱状图",
            "description": "生成随机数据，然后用柱状图展示",
            "data_request": "Generate 10 random numbers between 20 and 80",
            "plot_request": "Create a bar chart with this data, title 'Random Data Distribution'"
        },
        {
            "title": "销售数据趋势图",
            "description": "生成销售数据，然后用折线图展示趋势",
            "data_request": "Generate sales data for Q1, Q2, Q3 quarters, 6 products per quarter",
            "plot_request": "Create a line chart for average sales per quarter, title 'Quarterly Sales Trend'"
        },
        {
            "title": "多季度对比图",
            "description": "生成多季度数据，然后创建对比图表",
            "data_request": "Generate sales data for Spring, Summer, Autumn quarters, 4 products per quarter",
            "plot_request": "Create a comparison chart showing sales data for the three quarters, title 'Quarterly Sales Comparison'"
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