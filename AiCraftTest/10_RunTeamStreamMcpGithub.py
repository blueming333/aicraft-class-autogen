import os
import asyncio
import pathlib
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
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


async def main() -> None:
    # 获取当前脚本的绝对路径
    current_file = pathlib.Path(__file__).resolve()
    # 获取utils目录中mcp_server_github.py的绝对路径
    mcp_server_path = current_file.parent / "utils" / "mcp_server_github.py"
    
    # 确保路径存在
    if not mcp_server_path.exists():
        raise FileNotFoundError(f"GitHub MCP服务器文件未找到: {mcp_server_path}")
    
    print(f"使用GitHub MCP服务器路径: {mcp_server_path}")
    
    # 创建MCP服务器参数，并传递环境变量
    env = os.environ.copy()
    # 确保GITHUB_TOKEN环境变量被正确传递给子进程
    github_mcp_server = StdioServerParams(
        command="python", 
        args=[str(mcp_server_path)],
        env=env  # 传递包含GITHUB_TOKEN的环境变量
    )
    
    # 获取MCP工具
    try:
        tools = await mcp_server_tools(github_mcp_server)
        print(f"成功加载GitHub MCP工具: {len(tools)} 个工具可用")
    except Exception as e:
        print(f"加载GitHub MCP工具失败: {e}")
        return

    # 定义Agent
    agent = AssistantAgent(
        name="github_agent",
        model_client=model_client,
        system_message="""你是一个专门帮助用户查询和处理GitHub信息的AI助手。你可以搜索存储库、获取文件内容、查看代码等。

重要提示：使用github_search工具时，需要正确构造search_params参数，例如：
{
  "search_params": {
    "query": "MCP server fetch",
    "type": "code",
    "per_page": 5,
    "page": 1
  }
}

确保直接提供query字段，而不是使用q或其他字段名。

记住任务完成后回复'AiCraft结束'。""",
        model_client_stream=True,
        tools=tools,
        reflect_on_tool_use=True
    )

    # 定义终止条件，如果提到特定文本则终止对话
    text_termination = TextMentionTermination("AiCraft结束")

    # 定义Team，类型选择为RoundRobinGroupChat
    github_team = RoundRobinGroupChat(
        participants=[agent], 
        termination_condition=text_termination, 
        max_turns=None
    )

    # 运行team，下面是几个不同的示例任务，可以取消注释来测试不同功能
    
    # 1. 查询存储库信息
    # task = "获取'https://github.com/blueming333/aicraft-class-autogen.git'存储库的的今日最新5次提交记录"
    
    # 2. 搜索特定代码
    task = "搜索GitHub上与'MCP server fetch'相关的代码，并简要描述几个最相关的结果"
    
    # 3. 查看特定文件内容
    # task = "获取microsoft/autogen存储库中README.md文件的内容并总结主要功能"
    
    # 4. 对比两个分支
    # task = "列出microsoft/autogen存储库的主要分支，并解释它们的用途"

    print(f"执行任务: {task}")
    stream = github_team.run_stream(task=task)
    await Console(stream)


if __name__ == '__main__':
    # 运行main
    asyncio.run(main()) 