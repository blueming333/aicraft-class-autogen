# DeepSeek JSON Output 功能详细演示脚本
# 本脚本详细演示：
# 1. DeepSeek JSON Output 基础概念与应用场景
# 2. JSON Output 核心参数与配置方法
# 3. 简单 JSON 输出示例（中文场景）
# 4. 复杂 JSON 结构设计与实现
# 5. 错误处理与最佳实践
# 6. 实际应用场景演示

import json
import os
from openai import OpenAI
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

# ====================================================================
# 1. DeepSeek JSON Output 基础概念与应用场景
# ====================================================================

"""
DeepSeek JSON Output 功能介绍：

核心功能：
- 确保模型输出严格符合 JSON 格式
- 实现结构化数据输出，便于程序解析
- 支持复杂嵌套的 JSON 结构
- 提高数据处理的可靠性和一致性

主要应用场景：
1. 数据提取：从非结构化文本中提取结构化信息
2. 内容分析：情感分析、关键词提取、分类标签
3. 问答系统：结构化问答对生成
4. 数据转换：格式转换、数据清洗
5. API 集成：为下游系统提供标准化数据接口
6. 智能表单：自动填写和验证表单数据

技术优势：
- 输出格式可控性强
- 便于程序化处理
- 减少解析错误
- 提高系统集成效率
"""

# ====================================================================
# 2. JSON Output 核心参数与配置方法
# ====================================================================

@dataclass
class DeepSeekConfig:
    """
    DeepSeek 配置类
    封装API调用的核心参数
    """
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 4000
    temperature: float = 0.7

class DeepSeekJsonDemo:
    """
    DeepSeek JSON Output 演示类
    """
    
    def __init__(self, config: DeepSeekConfig):
        """
        初始化 DeepSeek 客户端
        
        关键配置说明：
        - response_format: {'type': 'json_object'} - 启用JSON输出模式
        - max_tokens: 设置足够大的值，防止JSON被截断
        - temperature: 控制输出的随机性，建议使用较低值确保稳定性
        """
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.config = config
        
    def _make_request(self, messages: List[Dict], response_format: Dict = None) -> str:
        """
        统一的API请求方法
        
        重要注意事项：
        1. system 或 user prompt 中必须包含 "json" 关键词
        2. 必须提供JSON格式示例来指导模型输出
        3. 合理设置 max_tokens 防止截断
        4. API有概率返回空content，需要异常处理
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                response_format=response_format or {'type': 'json_object'},
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("API返回空内容，请尝试修改prompt")
                
            return content
            
        except Exception as e:
            print(f"API请求失败: {e}")
            return "{}"

# ====================================================================
# 3. 简单 JSON 输出示例（中文场景）
# ====================================================================

    def demo_simple_qa_extraction(self):
        """
        示例1：简单问答对提取（中文）
        
        场景：从中文问答文本中提取结构化的问题和答案
        """
        print("=" * 60)
        print("示例1：简单问答对提取（中文场景）")
        print("=" * 60)
        
        system_prompt = """
        用户会提供一些中文的问答文本，请解析出"问题"和"答案"，并以JSON格式输出。

        示例输入：
        中国的首都是哪里？北京是中国的首都。

        示例JSON输出：
        {
            "question": "中国的首都是哪里？",
            "answer": "北京是中国的首都"
        }
        """

        user_prompt = "世界上最高的山峰是什么？珠穆朗玛峰是世界上最高的山峰，海拔8848.86米。"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        print(f"输入文本: {user_prompt}")
        print("\n正在调用DeepSeek API...")
        
        result = self._make_request(messages)
        
        try:
            parsed_result = json.loads(result)
            print("\n解析结果:")
            print(json.dumps(parsed_result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始输出: {result}")

# ====================================================================
# 4. 复杂 JSON 结构设计与实现
# ====================================================================

    def demo_complex_article_analysis(self):
        """
        示例2：复杂文章分析（多层级JSON结构）
        
        场景：分析新闻文章，提取多维度信息
        包含：基本信息、内容分析、关键实体、情感分析等
        """
        print("\n" + "=" * 60)
        print("示例2：复杂文章分析（多层级JSON结构）")
        print("=" * 60)
        
        system_prompt = """
        请分析用户提供的中文新闻文章，提取全面的结构化信息，以JSON格式输出。

        输出JSON格式示例：
        {
            "basic_info": {
                "title": "文章标题",
                "summary": "文章摘要（50字以内）",
                "word_count": 估算字数,
                "reading_time": "预估阅读时间（分钟）"
            },
            "content_analysis": {
                "main_topic": "主要话题",
                "key_points": [
                    "关键点1",
                    "关键点2",
                    "关键点3"
                ],
                "article_type": "文章类型（新闻/评论/分析等）"
            },
            "entities": {
                "persons": ["人物1", "人物2"],
                "organizations": ["机构1", "机构2"],
                "locations": ["地点1", "地点2"],
                "dates": ["日期1", "日期2"]
            },
            "sentiment_analysis": {
                "overall_sentiment": "正面/中性/负面",
                "confidence_score": 0.85,
                "emotional_keywords": ["关键情感词1", "关键情感词2"]
            },
            "tags": ["标签1", "标签2", "标签3"],
            "metadata": {
                "analysis_time": "分析时间",
                "language": "zh-CN",
                "complexity_level": "简单/中等/复杂"
            }
        }
        """

        user_prompt = """
        请分析以下新闻文章：

        标题：人工智能技术在医疗领域取得重大突破

        内容：近日，清华大学与北京协和医院联合研发的AI诊断系统在肺癌早期检测方面取得了重大突破。该系统通过深度学习算法分析CT影像，能够在几分钟内完成诊断，准确率高达95%。

        据项目负责人张教授介绍，这项技术已经在多家三甲医院进行了临床试验，预计明年上半年将正式投入使用。这一突破将大大提高肺癌早期发现率，为患者争取更多治疗时间。

        业界专家普遍认为，这项技术的成功应用标志着中国在医疗AI领域达到了国际先进水平，对于推动智慧医疗发展具有重要意义。
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        print("输入文章：")
        print(user_prompt[:100] + "...")
        print("\n正在进行复杂分析...")
        
        result = self._make_request(messages)
        
        try:
            parsed_result = json.loads(result)
            print("\n详细分析结果:")
            print(json.dumps(parsed_result, ensure_ascii=False, indent=2))
            
            # 结果验证和展示
            self._validate_complex_structure(parsed_result)
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始输出: {result}")

    def _validate_complex_structure(self, data: Dict):
        """
        验证复杂JSON结构的完整性
        """
        print("\n" + "-" * 40)
        print("结构验证结果:")
        
        required_keys = [
            'basic_info', 'content_analysis', 'entities', 
            'sentiment_analysis', 'tags', 'metadata'
        ]
        
        for key in required_keys:
            if key in data:
                print(f"✓ {key}: 存在")
            else:
                print(f"✗ {key}: 缺失")

    def demo_product_review_analysis(self):
        """
        示例3：商品评论深度分析
        
        场景：电商平台商品评论的多维度分析
        提取：评分、优缺点、推荐度、用户画像等
        """
        print("\n" + "=" * 60)
        print("示例3：商品评论深度分析")
        print("=" * 60)
        
        system_prompt = """
        请分析用户提供的商品评论，进行深度的结构化分析，以JSON格式输出。

        输出JSON格式：
        {
            "review_analysis": {
                "overall_rating": 4.5,
                "satisfaction_level": "满意/一般/不满意",
                "review_length": "简短/中等/详细",
                "authenticity_score": 0.9
            },
            "product_evaluation": {
                "advantages": [
                    {
                        "aspect": "功能特性",
                        "description": "具体优点描述",
                        "importance": "高/中/低"
                    }
                ],
                "disadvantages": [
                    {
                        "aspect": "功能特性",
                        "description": "具体缺点描述",
                        "severity": "严重/一般/轻微"
                    }
                ],
                "key_features_mentioned": ["特性1", "特性2"],
                "comparison_products": ["对比产品1", "对比产品2"]
            },
            "user_profile": {
                "experience_level": "新手/中级/专家",
                "usage_scenario": "使用场景描述",
                "purchase_motivation": "购买动机",
                "demographic_hints": {
                    "age_group": "年龄段推测",
                    "occupation_hints": "职业线索"
                }
            },
            "recommendation": {
                "would_recommend": true,
                "target_audience": "适合人群",
                "purchase_advice": "购买建议",
                "alternative_suggestions": ["替代产品建议"]
            },
            "sentiment_details": {
                "emotional_tone": "积极/中性/消极",
                "specific_emotions": ["具体情感1", "具体情感2"],
                "complaint_level": "无/轻微/严重"
            }
        }
        """

        user_prompt = """
        请分析以下商品评论：

        商品：iPhone 15 Pro Max
        评论：作为一个摄影爱好者，我对这款手机的相机功能非常满意。三摄系统的表现超出预期，特别是夜景模式，比我之前用的华为P50 Pro还要好。钛合金机身手感很棒，轻了不少。

        不过说实话，价格确实有点贵，而且电池续航比宣传的要差一些，重度使用一天下来需要充电两次。另外发热问题也存在，玩游戏半小时就比较明显了。

        总的来说，如果你预算充足且对拍照有较高要求，这款手机还是值得入手的。对于普通用户来说，iPhone 14可能更具性价比。
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        print("商品评论分析中...")
        
        result = self._make_request(messages)
        
        try:
            parsed_result = json.loads(result)
            print("\n评论深度分析结果:")
            print(json.dumps(parsed_result, ensure_ascii=False, indent=2))
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始输出: {result}")

# ====================================================================
# 5. 错误处理与最佳实践
# ====================================================================

    def demo_error_handling(self):
        """
        示例4：错误处理与异常情况演示
        
        展示各种可能的错误情况及处理方法
        """
        print("\n" + "=" * 60)
        print("示例4：错误处理与异常情况演示")
        print("=" * 60)
        
        # 错误情况1：prompt中缺少JSON关键词
        print("1. 测试缺少JSON关键词的prompt:")
        
        bad_system_prompt = """
        请分析用户输入的文本，提取关键信息。
        """  # 注意：这里故意不包含"json"关键词
        
        user_prompt = "北京是中国的首都。"
        
        messages = [
            {"role": "system", "content": bad_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            result = self._make_request(messages)
            print(f"结果: {result}")
            print("提示：虽然设置了JSON模式，但prompt中缺少'json'关键词可能导致输出不稳定")
        except Exception as e:
            print(f"错误: {e}")

        # 错误情况2：JSON格式示例不清晰
        print("\n2. 测试JSON格式示例不清晰的情况:")
        
        unclear_system_prompt = """
        请以json格式输出，包含一些信息。
        """  # 注意：JSON格式说明过于模糊
        
        messages = [
            {"role": "system", "content": unclear_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            result = self._make_request(messages)
            print(f"结果: {result}")
            print("提示：JSON格式示例不明确可能导致输出结构不一致")
        except Exception as e:
            print(f"错误: {e}")

    def best_practices_demo(self):
        """
        最佳实践演示
        """
        print("\n" + "=" * 60)
        print("DeepSeek JSON Output 最佳实践")
        print("=" * 60)
        
        best_practices = {
            "prompt_design": [
                "在system或user prompt中明确包含'json'关键词",
                "提供清晰、具体的JSON格式示例",
                "使用详细的字段说明和数据类型",
                "给出具体的输出值示例而非占位符"
            ],
            "parameter_settings": [
                "设置response_format为{'type': 'json_object'}",
                "max_tokens设置足够大，防止JSON截断",
                "temperature适当降低以确保输出稳定性",
                "考虑使用较低的top_p值"
            ],
            "error_handling": [
                "检查API响应的content是否为空",
                "验证返回的JSON格式是否正确",
                "实现重试机制处理偶发性失败",
                "记录和分析失败案例以优化prompt"
            ],
            "performance_optimization": [
                "缓存常用的prompt模板",
                "批量处理多个请求",
                "监控API调用频率和成本",
                "定期评估输出质量"
            ]
        }
        
        for category, practices in best_practices.items():
            print(f"\n{category.upper()}:")
            for i, practice in enumerate(practices, 1):
                print(f"  {i}. {practice}")

# ====================================================================
# 6. 实际应用场景演示
# ====================================================================

def main():
    """
    主函数：运行所有演示示例
    """
    print("DeepSeek JSON Output 功能演示")
    print("=" * 80)
    
    # 配置信息（请替换为您的实际API密钥）
    config = DeepSeekConfig(
        api_key="your-api-key-here",  # 请替换为您的API密钥
        max_tokens=4000,
        temperature=0.3  # 较低的温度确保输出稳定
    )
    
    # 检查API密钥
    if config.api_key == "your-api-key-here":
        print("⚠️  请先配置您的DeepSeek API密钥")
        print("   在代码中将 'your-api-key-here' 替换为您的实际API密钥")
        print("   或设置环境变量 DEEPSEEK_API_KEY")
        
        # 尝试从环境变量获取
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if api_key:
            config.api_key = api_key
            print("✓ 已从环境变量获取API密钥")
        else:
            print("\n演示程序将以模拟模式运行（不会实际调用API）")
            return
    
    # 创建演示实例
    demo = DeepSeekJsonDemo(config)
    
    try:
        # 运行各个演示
        demo.demo_simple_qa_extraction()
        demo.demo_complex_article_analysis()
        demo.demo_product_review_analysis()
        demo.demo_error_handling()
        demo.best_practices_demo()
        
        print("\n" + "=" * 80)
        print("演示完成！")
        # print("\n要运行此演示，请：")
        # print("1. 安装依赖：pip install openai")
        # print("2. 设置API密钥：export DEEPSEEK_API_KEY='your-api-key'")
        # print("3. 运行脚本：python FastAPIDemo4_DeepSeekJsonOutput.py")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        print("请检查网络连接和API密钥配置")

if __name__ == "__main__":
    main()

# ====================================================================
# 附录：使用说明和扩展建议
# ====================================================================

"""
使用说明：

1. 环境准备：
   - Python 3.7+
   - pip install openai
   - 获取DeepSeek API密钥

2. 运行方式：
   # 方式1：直接运行
   python FastAPIDemo4_DeepSeekJsonOutput.py
   
   # 方式2：设置环境变量
   export DEEPSEEK_API_KEY='your-api-key'
   python FastAPIDemo4_DeepSeekJsonOutput.py

3. 扩展建议：
   - 集成到FastAPI应用中提供JSON化API
   - 添加数据库存储解析结果
   - 实现批量文本处理功能
   - 集成前端界面进行可视化展示
   - 添加不同领域的专业模板

4. 注意事项：
   - API调用有频率限制，注意控制调用频次
   - JSON输出可能不完整，需要验证和重试机制
   - 不同prompt可能产生不同质量的结果，需要调优
   - 成本控制：合理设置max_tokens避免不必要的开销
""" 