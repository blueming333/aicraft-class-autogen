# MCP服务器功能详解 - mcp_server_fetch.py

`mcp_server_fetch.py`是一个基于MCP(Model Context Protocol)协议的网页内容获取服务器，它在AutoGen项目中扮演着非常重要的角色。下面详细介绍它的实现逻辑和解决的问题：

## 功能概述

这个脚本主要解决了AI智能体访问互联网的问题，允许智能体获取网页内容并以结构化方式处理，使其能够：

1. 从互联网抓取最新信息
2. 将HTML内容转换为Markdown格式，便于模型理解
3. 遵循robots.txt规则，合规地抓取网站

## 核心实现逻辑

### 1. MCP协议集成

MCP(Model Context Protocol)是一种用于模型与外部工具交互的协议标准。脚本通过以下方式实现了MCP协议：

- 创建了`Server`实例，定义了工具和提示接口
- 使用`stdio_server`进行标准输入输出通信
- 定义了`list_tools`、`list_prompts`、`call_tool`和`get_prompt`处理函数

### 2. 网页内容处理流程

当智能体请求抓取网页时，处理流程如下：

1. **URL验证**：检查URL格式是否合法
2. **robots.txt检查**：通过`check_may_autonomously_fetch_url`函数检查是否允许抓取
3. **内容获取**：通过`fetch_url`函数使用`httpx`库异步抓取网页内容
4. **内容转换**：
   - 对HTML内容，使用`readabilipy`提取主要内容，再用`markdownify`转为Markdown
   - 对非HTML内容，保留原始格式返回
5. **内容管理**：处理长内容截断、分页获取等情况

### 3. 关键组件

#### URL内容获取与简化

```python
async def fetch_url(url: str, user_agent: str, force_raw: bool = False) -> Tuple[str, str]:
    # 使用httpx异步获取网页内容
    # 判断内容类型并进行相应处理
    # 返回处理后的内容和前缀信息
```

#### HTML转Markdown

```python
def extract_content_from_html(html: str) -> str:
    # 使用readabilipy提取主要内容
    # 使用markdownify将HTML转为Markdown
    # 返回简化后的内容
```

#### robots.txt合规检查

```python
async def check_may_autonomously_fetch_url(url: str, user_agent: str) -> None:
    # 获取robots.txt URL
    # 检查robots.txt规则
    # 不允许抓取时抛出异常
```

## 解决的问题

### 1. 智能体互联网访问能力

传统LLM模型通常没有实时访问互联网的能力，只能依赖训练数据中的知识。`mcp_server_fetch.py`解决了这一限制，使得智能体能够：

- 获取最新信息和数据
- 访问训练数据中不存在的内容
- 引用具体来源而非依赖预训练知识

### 2. 内容可读性和结构化

网页内容通常含有大量HTML标签、样式和脚本，对模型理解造成困难。脚本通过：

- 提取主要内容，过滤广告、导航等无关元素
- 将内容转换为Markdown格式，保留基本结构但去除复杂标签
- 处理过长内容，提供分段获取能力

### 3. 网络爬取合规性

网站通常有爬虫访问规则，脚本通过以下方式确保合规：

- 解析robots.txt文件
- 使用合适的User-Agent标识
- 尊重网站对自动抓取的限制
- 提供手动模式作为备选方案

## 在AutoGen项目中的应用

在`BasicTest/8_RunTeamStreamMCP.py`中，该脚本被集成到智能体系统中：

```python
# 创建MCP服务器参数
fetch_mcp_server = StdioServerParams(command="python", args=[str(mcp_server_path)])
# 获取MCP工具
tools = await mcp_server_tools(fetch_mcp_server)

# 将工具提供给Agent
agent = AssistantAgent(
    name="agent",
    model_client=model_client,
    system_message="你是一个乐于助人的AI智能助手。...",
    tools=tools,
    reflect_on_tool_use=True
)
```

这使得Agent能够在对话过程中访问网页内容，例如：

```python
# 让智能体概述网站内容
stream = reflection_team.run_stream(task="概述 https://www.emqx.com/zh 的内容")
```

## 技术亮点

1. **异步处理**：全面使用`async/await`进行异步网络请求，提高效率
2. **错误处理**：完善的错误处理机制，提供清晰的错误信息
3. **灵活配置**：支持自定义User-Agent和robots.txt处理策略
4. **内容分页**：通过`start_index`和`max_length`参数支持长内容分段获取
5. **模式选择**：提供原始模式(`raw=True`)和简化模式，适应不同需求

总的来说，`mcp_server_fetch.py`是一个强大的工具，让AutoGen智能体拥有了"眼睛"，能够看到互联网上的实时信息，大大扩展了智能体的能力边界，同时保持了对网站爬取规则的尊重。 