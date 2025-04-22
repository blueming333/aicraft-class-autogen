import os
import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from dotenv import load_dotenv
from autogen_agentchat.base import Handoff
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
        "family": ModelFamily.R1,
    },
    max_tokens=4096,
)


# 定义标准input函数，直接从控制台读取用户输入
def console_input(prompt):
    # 打印提示信息
    print(f"\n{prompt} (请在控制台输入您的回复): ")
    # 从控制台读取用户输入
    user_input = input(">>> ")
    return user_input


async def main() -> None:
    # 定义Agent
    weather_agent = AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        description="一个和用户交互的智能体。",
        handoffs=[Handoff(target="user", message="移交给用户。")],        
    )

    # 定义Agent - 使用人类用户真实输入
    user_proxy = UserProxyAgent(
        name="user_proxy",
        input_func=console_input  # 使用从控制台读取的输入
    )

    # 定义终止条件  如果提到特定文本则终止对话
    text_termination = TextMentionTermination("AiCraft结束")
    # 定义终止条件，在5条信息后停止任务
    max_message_termination = MaxMessageTermination(4)
    # 使用`|` 运算符组合终止条件，在满足任一条件时停止任务
    termination = text_termination | max_message_termination

    # 定义Team Team的类型选择为RoundRobinGroupChat
    agent_team = RoundRobinGroupChat(participants=[weather_agent,user_proxy], termination_condition=termination, max_turns=None)

    # 运行team并使用官方提供的Console工具以适当的格式输出
    stream = agent_team.run_stream(task="上海的天气如何?")
    await Console(stream)


if __name__ == '__main__':
    # 运行main
    asyncio.run(main())