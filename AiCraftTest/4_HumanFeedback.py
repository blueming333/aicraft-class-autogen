import os
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.conditions import TextMentionTermination, HandoffTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from dotenv import load_dotenv
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
    model="qwen-plus",
     model_info={
        "function_calling": True,
        "json_output": False,
        "vision": False,
        "stream": True,
        "family": ModelFamily.R1,
    },
)


async def main() -> None:
    # 定义Agent
    weather_agent = AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        description="一个和用户交互的智能体。",
        system_message="不知道答案时，一定要转给用户。任务完成后回复“AiCraft”",
        handoffs=[Handoff(target="user", message="移交给用户。")],
    )

    # 定义终止条件  如果提到特定文本则终止对话
    text_termination = TextMentionTermination("AiCraft")
    # 定义终止条件  在Agent发送HandoffMessage消息时终止对话
    handoff_termination = HandoffTermination(target="user")
    # 使用`|` 运算符组合终止条件，在满足任一条件时停止任务
    termination = handoff_termination | text_termination

    # 定义Team Team的类型选择为RoundRobinGroupChat
    agent_team = RoundRobinGroupChat(participants=[weather_agent], termination_condition=termination, max_turns=None)

    # 运行team并使用官方提供的Console工具以适当的格式输出
    stream = agent_team.run_stream(task="上海的天气如何?")
    await Console(stream)

    # 运行team并使用官方提供的Console工具以适当的格式输出
    stream = agent_team.run_stream(task="上海正在下雨,天气很糟糕。")
    await Console(stream)


if __name__ == '__main__':
    # 运行main
    asyncio.run(main())