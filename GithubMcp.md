# MCP服务器功能详解 - mcp_server_github.py

`mcp_server_github.py`是一个基于MCP(Model Context Protocol)协议的GitHub接口服务器，它在AutoGen项目中提供了强大的代码仓库访问能力。下面详细介绍它的实现逻辑和解决的问题：

## 功能概述

这个脚本主要解决了AI智能体访问GitHub代码平台的问题，允许智能体与代码仓库交互，具体功能包括：

1. 获取存储库的基本信息和统计数据
2. 查看文件内容和目录结构
3. 搜索代码、仓库、问题等GitHub资源
4. 查看分支、提交历史和特定提交详情
5. 获取README文件内容

## 核心实现逻辑

### 1. MCP协议集成

脚本通过以下方式实现了MCP协议的集成：

- 创建`Server`实例，注册工具和提示接口
- 使用`stdio_server`进行标准输入输出通信
- 通过装饰器定义`list_tools`、`call_tool`和`list_prompts`处理函数

### 2. GitHub API交互

脚本核心是`GitHubClient`类，它封装了与GitHub API的所有交互：

```python
class GitHubClient:
    """GitHub API客户端"""
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        # 初始化客户端，设置认证信息
        # 支持通过环境变量获取GitHub令牌
    
    async def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, json_data: Dict = None) -> Dict:
        # 发送API请求，处理认证和错误
        # 支持GET/POST等请求方法
```

### 3. 数据模型与参数验证

脚本使用Pydantic模型实现参数验证和类型安全：

```python
class RepoInfo(BaseModel):
    """存储库信息模型"""
    name: str
    owner: Any
    full_name: str = ""
    description: Optional[str] = None
    # 其他字段...
    
    @validator('full_name', pre=True, always=True)
    def set_full_name(cls, v, values):
        # 数据验证和转换逻辑
```

这确保了API请求参数的正确性和一致性。

### 4. 工具函数实现

脚本为每个GitHub操作实现了专门的方法：

#### 获取仓库信息

```python
async def get_repo(self, owner: str, repo: str) -> RepoInfo:
    """获取存储库信息"""
    endpoint = f"/repos/{owner}/{repo}"
    data = await self._make_request(endpoint)
    return RepoInfo(**data)
```

#### 文件内容获取与解码

```python
async def get_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> FileContent:
    """获取文件内容"""
    # 获取文件信息
    # 解码Base64编码的内容
    # 处理二进制文件
```

#### 提交历史查询

```python
async def list_commits(self, owner: str, repo: str, sha: Optional[str] = None, path: Optional[str] = None, page: int = 1, per_page: int = 30) -> List[Dict]:
    """获取存储库的提交历史"""
    # 构建API请求
    # 支持按分支、路径过滤
    # 支持分页获取
```

## 解决的问题

### 1. 代码获取与分析能力

传统LLM缺乏直接访问代码仓库的能力，该脚本使得智能体能够：

- 检索最新代码库内容
- 分析代码结构和实现逻辑
- 查看代码演变历史和提交记录

### 2. 结构化API调用

GitHub API较为复杂，脚本提供了友好的接口：

- 统一的错误处理和异常转换
- 参数验证和类型检查
- 结果格式化，将JSON转为人类可读的表格和列表

### 3. 认证与访问控制

脚本解决了GitHub API访问限制问题：

- 支持通过环境变量配置认证令牌
- 处理API速率限制
- 适当的错误消息和重试策略

## 在AutoGen项目中的应用

在`BasicTest/10_RunTeamStreamMcpGithub.py`中，该脚本被集成到智能体系统中：

```python
# 获取当前脚本的绝对路径
current_file = pathlib.Path(__file__).resolve()
# 获取mcp_server_github.py的绝对路径
mcp_server_path = current_file.parent / "utils" / "mcp_server_github.py"
    
# 创建MCP服务器参数
github_mcp_server = StdioServerParams(command="python", args=[str(mcp_server_path)])
    
# 获取MCP工具
tools = await mcp_server_tools(github_mcp_server)

# 将工具提供给Agent
agent = AssistantAgent(
    name="github_agent",
    model_client=model_client,
    system_message="你是一个专门帮助用户查询和处理GitHub信息的AI助手...",
    tools=tools,
    reflect_on_tool_use=True
)
```

这使得Agent能够在对话中查询和使用GitHub信息，例如：

```python
# 获取存储库的最新提交信息
task = "获取'https://github.com/blueming333/aicraft-class-autogen.git'存储库的最新3次提交的内容"
```

## 主要工具集

该脚本提供了以下核心工具：

1. **get_repo** - 获取仓库基本信息（星标数、Fork数、语言等）
2. **get_file_content** - 获取特定文件的内容
3. **list_directory** - 列出目录结构
4. **github_search** - 搜索GitHub内容（代码、仓库等）
5. **list_branches** - 列出仓库的分支
6. **get_readme** - 获取README文件
7. **list_commits** - 获取提交历史
8. **get_commit** - 获取特定提交的详情

## 技术亮点

1. **异步实现**：全面使用`async/await`进行异步API请求，提高效率
2. **优雅的结果格式化**：将API响应转换为Markdown表格和结构化文本
3. **灵活的过滤和查询**：支持按分支、路径、SHA等多种条件筛选
4. **错误处理**：提供清晰的错误信息和友好的错误展示
5. **分页支持**：处理大量结果的分页获取

总的来说，`mcp_server_github.py`为AutoGen智能体提供了"代码视野"，使其能够理解、分析和操作GitHub上的代码仓库，极大地扩展了智能体在代码分析、问题解决和开发辅助方面的能力。 