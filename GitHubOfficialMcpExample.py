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
    model="qwen-plus-2025-01-25",  # 使用阿里千问，支持函数调用
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
    # 配置GitHub官方MCP服务器
    # 假设已经安装了GitHub官方MCP服务器
    # 可以通过go install github.com/github/github-mcp-server/cmd/mcp-server-github@latest 安装
    
    # 检查是否安装了GitHub MCP服务器
    try:
        import subprocess
        result = subprocess.run(["which", "mcp-server-github"], capture_output=True, text=True)
        github_mcp_path = result.stdout.strip()
        
        if not github_mcp_path:
            print("GitHub官方MCP服务器未找到，请先安装。")
            print("可以通过以下命令安装：go install github.com/github/github-mcp-server/cmd/mcp-server-github@latest")
            return
            
        print(f"找到GitHub MCP服务器: {github_mcp_path}")
    except Exception as e:
        print(f"检查GitHub MCP服务器失败: {e}")
        print("请确保已安装GitHub官方MCP服务器")
        return
    
    # 创建MCP服务器参数，使用官方GitHub MCP服务器
    env = os.environ.copy()
    # GitHub官方MCP服务器会自动使用GITHUB_TOKEN环境变量
    github_mcp_server = StdioServerParams(
        command=github_mcp_path,  # 使用GitHub官方MCP服务器路径
        args=[],  # GitHub官方MCP服务器不需要额外参数
        env=env   # 传递环境变量，包括GITHUB_TOKEN
    )
    
    # 获取MCP工具
    try:
        tools = await mcp_server_tools(github_mcp_server)
        print(f"成功加载GitHub官方MCP工具: {len(tools)} 个工具可用")
        
        # 打印可用工具列表
        print("可用工具:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"加载GitHub官方MCP工具失败: {e}")
        return

    # 定义Agent
    agent = AssistantAgent(
        name="github_official_agent",
        model_client=model_client,
        system_message="""你是一个专门帮助用户查询和处理GitHub信息的AI助手。你可以搜索存储库、获取文件内容、查看代码等。

你使用的是GitHub官方提供的MCP服务器，可以进行更全面的GitHub操作，包括:
1. 搜索代码和存储库
2. 获取文件内容和存储库信息
3. 创建和更新文件
4. 列出和获取分支、提交信息
5. 创建拉取请求等功能

当使用search_repositories工具搜索存储库时，使用以下格式：
{
  "query": "你的搜索查询",
  "sort": "stars",  # 可选: stars, forks, updated
  "order": "desc",  # 可选: desc, asc
  "page": 1,         # 可选
  "perPage": 5       # 可选
}

当使用search_code工具搜索代码时，使用以下格式：
{
  "query": "你的搜索查询 language:python",
  "sort": "best-match",  # 可选
  "order": "desc",       # 可选: desc, asc
  "page": 1,              # 可选
  "perPage": 5            # 可选
}

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

    # 运行team，下面是几个不同的示例任务
    available_tasks = [
        "获取'github/github-mcp-server'存储库的信息和最新5次提交记录",
        "搜索GitHub上与'MCP server'相关的代码，并简要描述几个最相关的结果",
        "获取'github/github-mcp-server'存储库中README.md文件的内容",
        "列出'github/github-mcp-server'存储库的主要分支",
        "搜索GitHub上星标数超过1000的Python AI项目",
    ]
    
    # 打印可用任务列表
    print("\n可用示例任务:")
    for i, task in enumerate(available_tasks):
        print(f"{i+1}. {task}")
    
    # 让用户选择任务或输入自定义任务
    try:
        choice = input("\n请选择任务编号，或直接输入自定义任务: ")
        if choice.isdigit() and 1 <= int(choice) <= len(available_tasks):
            task = available_tasks[int(choice)-1]
        else:
            task = choice
    except Exception:
        task = available_tasks[0]  # 默认使用第一个任务

    print(f"\n执行任务: {task}")
    stream = github_team.run_stream(task=task)
    await Console(stream)


if __name__ == '__main__':
    # 运行main
    asyncio.run(main()) 