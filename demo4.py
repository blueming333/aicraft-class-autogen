import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_agentchat.ui import Console

# 创建架构师专用工具函数
async def generate_architecture_patterns(project_type: str) -> str:
    """根据项目类型生成架构模式建议"""
    patterns = {
        "web应用": "MVC架构、微服务架构、前后端分离、RESTful API设计",
        "移动应用": "MVVM架构、组件化架构、混合开发框架、原生开发",
        "数据处理": "ETL架构、流处理架构、批处理架构、数据湖架构",
        "AI系统": "模型服务架构、MLOps流水线、特征工程架构、推理服务架构",
        "游戏": "ECS架构、客户端-服务器架构、状态同步、帧同步架构"
    }
    
    # 根据项目类型匹配架构模式
    matched_patterns = []
    for key, value in patterns.items():
        if key in project_type or any(keyword in project_type for keyword in key.split()):
            matched_patterns.append(value)
    
    return f"推荐架构模式: {', '.join(matched_patterns) if matched_patterns else '分层架构、模块化设计、可扩展架构'}"

# 创建总监专用工具函数
async def evaluate_feasibility_factors(architecture: str) -> str:
    """评估架构方案的可行性因素"""
    factors = {
        "技术复杂度": "评估技术实现难度和团队技术栈匹配度",
        "开发成本": "估算开发时间、人力成本和技术债务",
        "维护成本": "分析后期维护、升级和扩展成本",
        "性能风险": "识别潜在性能瓶颈和扩展性问题",
        "安全风险": "评估安全漏洞和合规要求"
    }
    
    # 简化的可行性评估逻辑
    risk_indicators = []
    if "微服务" in architecture:
        risk_indicators.append("微服务复杂度较高，需要考虑服务治理")
    if "分布式" in architecture:
        risk_indicators.append("分布式系统需要处理网络延迟和一致性问题")
    if "AI" in architecture or "机器学习" in architecture:
        risk_indicators.append("AI系统需要考虑模型训练和推理资源")
    
    return f"可行性评估要点: {'; '.join(list(factors.values()))}。特别关注: {', '.join(risk_indicators) if risk_indicators else '无特殊风险'}"

# 创建OpenAI模型客户端
model_client = OpenAIChatCompletionClient(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key="sk-36a3fb92e2414794bd9785014e4a1d84",
    model_info={
        "function_calling": True,
        "json_output": True,
        "vision": False,
        "stream": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
    }
)

# 创建软件研发架构师Agent
architect_agent = AssistantAgent(
    name="Software_Architect",
    model_client=model_client,
    tools=[generate_architecture_patterns],
    system_message="""
    你是一位经验丰富的软件研发架构师。你的职责是根据输入的任务需求，设计合适的技术架构方案。

    工作要求：
    1. 仔细分析任务需求，理解业务场景和技术要求
    2. 设计合适的系统架构，包括：
       - 整体架构模式选择
       - 技术栈推荐
       - 模块划分和组件设计
       - 数据流和接口设计
       - 部署和运维考虑
    3. 输出清晰的架构设计文档，包含架构图说明
    4. 可以使用工具获取架构模式建议
    5. 确保方案具有可扩展性和可维护性

    请根据任务输入，提供详细的技术架构方案。
    """,
)

# 创建研发总监Agent
director_agent = AssistantAgent(
    name="Development_Director",
    model_client=model_client,
    tools=[evaluate_feasibility_factors],
    system_message="""
    你是一位资深的研发总监。你的职责是对架构师提出的技术方案进行全面的可行性评估。

    评估维度：
    1. 技术可行性：
       - 技术栈成熟度和稳定性
       - 团队技术能力匹配度
       - 技术风险评估
    2. 成本可行性：
       - 开发成本和时间估算
       - 运维和维护成本
       - 人力资源需求
    3. 业务可行性：
       - 是否满足业务需求
       - 性能和扩展性是否达标
       - 安全性和合规性考虑
    4. 风险评估：
       - 识别潜在风险点
       - 提出风险缓解措施
       - 制定备选方案

    请基于架构师的方案，输出详细的可行性评估报告，包含明确的结论和建议。
    """,
)

# 创建RoundRobinGroupChat团队
async def create_architecture_review_team():
    """创建架构评审团队"""
    team = RoundRobinGroupChat([architect_agent, director_agent])
    return team

async def run_architecture_review(task_description: str):
    """运行架构评审流程"""
    print(f"🏗️ 开始架构评审流程...")
    print(f"📋 任务描述: {task_description}")
    print("="*60)
    
    # 创建团队
    team = await create_architecture_review_team()
    
    # 构建任务消息
    task_message = f"""
    项目任务需求：{task_description}
    
    请按照以下流程进行：
    1. 架构师：根据任务需求设计技术架构方案
    2. 研发总监：对架构方案进行可行性评估
    
    请开始工作。
    """
    
    # 运行团队协作
    # result = await team.run(task=task_message)
    # 流式输出
    stream = team.run_stream(task=task_message)
    await Console(stream)


    
    print("\n" + "="*60)
    print("📊 架构评审完成")
    return result

# 示例使用
async def main():
    """主函数演示"""
    # 示例任务
    example_tasks = [
        "开发一个面向中小企业的在线项目管理平台，需要支持多租户、实时协作、移动端访问，预计用户规模1-10万",
        "构建一个智能客服系统，集成自然语言处理、知识图谱、多渠道接入，需要7x24小时稳定运行",
        "设计一个电商平台的推荐系统，需要实时个性化推荐、A/B测试能力、大数据处理，日活用户百万级别"
    ]
    
    print("🚀 欢迎使用架构评审系统！")
    print("系统包含：软件架构师 + 研发总监")
    print("流程：需求分析 → 架构设计 → 可行性评估")
    print("\n以下是示例演示：")
    
    # 选择一个示例进行演示
    selected_task = example_tasks[0]
    await run_architecture_review(selected_task)
    
    print("\n" + "="*60)
    print("💡 提示：您可以输入任何软件开发任务来获得架构方案和可行性评估")
    print("例如：'电商平台'、'数据分析系统'、'移动应用' 等")

# 如果直接运行此文件，执行示例
if __name__ == "__main__":
    asyncio.run(main())
