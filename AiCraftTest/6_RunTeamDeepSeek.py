import os
import asyncio
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily


# 加载.env文件中的环境变量
load_dotenv()

# 设置OpenAI API密钥和基础URL
os.environ.setdefault("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
# 使用.env文件中的API密钥，如果不存在则使用默认值
if not os.environ.get("OPENAI_API_KEY"):
    print("警告: 未找到OPENAI_API_KEY环境变量。请在.env文件中设置此变量。")

# 设置GitHub API密钥，如果有的话
github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    print("警告: 未找到GITHUB_TOKEN环境变量。某些GitHub API功能可能受限。")
else:
    print(f"成功加载GitHub令牌: {github_token[:4]}...{github_token[-4:]}")

# 定义LLM
model_client = OpenAIChatCompletionClient(
    model="qwen-plus",  # 使用阿里千问，支持函数调用
    model_info={
        "function_calling": True,
        "json_output": False,
        "vision": False,
        "stream": True,
        "family": ModelFamily.UNKNOWN,  # 使用未知模型家族
    },
    max_tokens=4096,
)


async def main() -> None:
    # 定义Agent
    primary_agent = AssistantAgent(
        name="primary",
        model_client=model_client,
        system_message="你是一个乐于助人的AI智能助手。",
        model_client_stream=True
    )

    # 定义Agent
    critic_agent = AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message='提供建设性反馈意见。记住只有当你的反馈意见得到处理后才允许回复 "AiCraft"。',
        model_client_stream=True
    )

    # 定义终止条件  如果提到特定文本则终止对话
    text_termination = TextMentionTermination("AiCraft")
    # 定义终止条件，在5条信息后停止任务
    max_message_termination = MaxMessageTermination(3)
    # 使用`|` 运算符组合终止条件，在满足任一条件时停止任务
    termination = text_termination | max_message_termination

    # 定义Team Team的类型选择为RoundRobinGroupChat
    reflection_team = RoundRobinGroupChat(
        participants=[primary_agent, critic_agent], 
        termination_condition=termination, 
        max_turns=None
    )

    # 1、运行team并使用官方提供的Console工具以适当的格式输出
    stream = reflection_team.run_stream(task="写一首七言绝句，关于秋天")
    await Console(stream)

    # # 2、运行team并使用流式输出，自己处理消息并将其流到前端
    # async for message in reflection_team.run_stream(task="写一首七言绝句，关于秋天"):
    #     print(message)


if __name__ == '__main__':
    # 运行main
    asyncio.run(main())

