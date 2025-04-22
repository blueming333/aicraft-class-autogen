import os
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_core.models import ModelFamily
import pathlib


os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
os.environ["OPENAI_API_KEY"] = "sk-bbac7524061c4acfb485f953e40212174f66"


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
    max_tokens=4096,
)


async def main() -> None:
    # 获取当前脚本的绝对路径
    current_file = pathlib.Path(__file__).resolve()
    # 获取utils目录中mcp_server_fetch.py的绝对路径
    mcp_server_path = current_file.parent / "utils" / "mcp_server_fetch.py"
    
    # 确保路径存在
    if not mcp_server_path.exists():
        raise FileNotFoundError(f"MCP服务器文件未找到: {mcp_server_path}")
    
    print(f"使用MCP服务器路径: {mcp_server_path}")
    
    # 使用绝对路径创建MCP服务器参数
    fetch_mcp_server = StdioServerParams(command="python", args=[str(mcp_server_path)])
    tools = await mcp_server_tools(fetch_mcp_server)

    # 定义Agent
    agent = AssistantAgent(
        name="agent",
        model_client=model_client,
        system_message="你是一个乐于助人的AI智能助手。记住任务完成后回复'AiCraft结束'。",
        model_client_stream=True,
        tools=tools,
        reflect_on_tool_use=True
    )


    # 定义终止条件  如果提到特定文本则终止对话
    text_termination = TextMentionTermination("AiCraft结束")

    # 定义Team Team的类型选择为RoundRobinGroupChat
    reflection_team = RoundRobinGroupChat(participants=[agent], termination_condition=text_termination, max_turns=None)

    # 1、运行team并使用官方提供的Console工具以适当的格式输出
    stream = reflection_team.run_stream(task="概述 https://www.emqx.com/zh 的内容")
    await Console(stream)

    # # 2、运行team并使用流式输出,自己处理消息并将其流到前端
    # async for message in reflection_team.run_stream(task="概述 https://en.wikipedia.org/wiki/Seattle 的内容"):
    #     print(message)


if __name__ == '__main__':
    # 运行main
    asyncio.run(main())

