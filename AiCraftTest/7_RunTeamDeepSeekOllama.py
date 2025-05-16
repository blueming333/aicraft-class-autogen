import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily

# 导入工具类
# from entity_tools import EntityTools


# 定义LLM
model_client = OllamaChatCompletionClient(
    model="qwen3:1.7b",
    api_key="placeholder",
    host="http://localhost:11434",
    model_info={
        "function_calling": True,  # 启用function calling
        "json_output": True,       # 启用JSON输出
        "vision": False,
        "family": ModelFamily.UNKNOWN,
    }
)


async def main() -> None:
    # 创建工具实例
    # entity_tools = EntityTools()
    
    # 定义Agent，并加载工具
    primary_agent = AssistantAgent(
        name="primary",
        model_client=model_client,
        system_message="你是一个乐于助人的AI智能助手。你可以使用format_task工具将用户的任务信息格式化为标准实体格式。",
        model_client_stream=True,
        # 为Agent添加工具
        # functions=[entity_tools.format_task]
    )

    # 定义Agent
    critic_agent = AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message="提供建设性反馈意见。记住只有当你的反馈意见得到处理后再允许回复 \"AiCraft结束\"。",
        model_client_stream=True
    )

    # 定义终止条件  如果提到特定文本则终止对话
    text_termination = TextMentionTermination("AiCraft结束")
    # 定义终止条件，在5条信息后停止任务
    max_message_termination = MaxMessageTermination(5)
    # 使用`|` 运算符组合终止条件，在满足任一条件时停止任务
    termination = text_termination | max_message_termination

    # 定义Team Team的类型选择为RoundRobinGroupChat
    reflection_team = RoundRobinGroupChat(participants=[primary_agent, critic_agent], termination_condition=termination, max_turns=None)

    # 1、运行team并使用官方提供的Console工具以适当的格式输出
    stream = reflection_team.run_stream(task="请帮我创建一个网站开发任务，需要在下周五前完成，优先级很高，主要是开发一个电商网站的支付模块")
    await Console(stream)

    # # 2、运行team并使用流式输出,自己处理消息并将其流到前端
    # async for message in reflection_team.run_stream(task="写一首关于秋季的短诗"):
    #     print(message)


if __name__ == '__main__':
    # 运行main
    asyncio.run(main())

