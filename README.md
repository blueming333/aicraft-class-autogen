# AI智能体课堂项目 - AutoGen多智能体协同开发

## 📚 课程介绍
本课程旨在教授学生如何使用微软开源的AutoGen框架开发多智能体协同系统。通过本课程，学生将学习到AI智能体的基本概念、AutoGen框架的核心功能以及如何构建多智能体协同完成复杂任务。

---

## 🔍 AutoGen框架介绍
AutoGen是微软发布的一个用于构建AI Agent系统和应用程序的开源框架

* **GitHub地址**: [https://github.com/microsoft/autogen](https://github.com/microsoft/autogen)
* **文档地址**: [https://microsoft.github.io/autogen/stable/index.html](https://microsoft.github.io/autogen/stable/index.html)

最新架构AutoGen v0.4正式发布第一个稳定版本。v0.4版本是对AutoGen的一次从头开始的重写，目的是为构建Agent创建一个更健壮、可扩展、更易用的跨语言库。

AutoGen v0.4的应用接口采用分层架构设计，存在多套软件接口用以满足不同的场景需求：

### 1. Magentic-One CLI
基于控制台的多Agent助手，用于执行基于Web和文件的任务。基于AgentChat构建。

### 2. Studio
一款无需编写代码即可进行原型设计和管理Agent的应用程序。基于AgentChat构建。

### 3. Core: 事件驱动型接口
核心接口(autogen-core)，用于构建可扩展的多Agent人工智能系统的事件驱动编程框架。

### 4. AgentChat: 任务驱动型应用接口
autogen-agentchat，用于构建会话式单Agent和多Agent应用程序的编程框架，建立在Core核心层之上，抽象了许多底层系统概念。

### 5. Extensions: 第三方系统接口
扩展包(autogen-ext)，与外部服务或其他库交互的Core和AgentChat组件的实现。可以查找并使用社区扩展或创建自己的社区扩展，如OpenAI模型客户端接口等。

---

## 📋 课程内容
本课程主要涵盖以下内容：

1. AI智能体基础概念和应用场景
2. AutoGen框架核心概念和架构
3. 单智能体开发与应用
4. 多智能体协同系统设计与实现
5. 工具集成与增强智能体能力
6. 实战项目开发

---

## 📁 项目结构
本项目包含了AutoGen框架的各种演示案例和实战练习：

- **BasicTest**: AgentChat框架基本功能测试
- **MagenticOneCli**: Magentic-One CLI使用示例
- **Extensions**: AutoGen扩展功能测试，包括LangChain工具、缓存系统等
- **GraphRAG**: 知识图谱增强检索生成系统集成示例

---

## 🛠️ 项目实践指南

## 1. 前期准备工作

### 1.1 开发环境搭建
您可以选择以下任一方式创建和管理Python虚拟环境：

#### Conda环境
提供跨平台的包和环境管理系统
- 从[Anaconda官网](https://www.anaconda.com/download/)下载并安装Anaconda或Miniconda
- 创建并激活虚拟环境
```bash
conda create -n autogen-env python=3.10
conda activate autogen-env
```

#### UV环境
更快的Python包管理器和虚拟环境工具
- 安装UV: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
```bash
# 使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv
source .venv/bin/activate  # Linux/macOS
# Windows: .venv\Scripts\activate
```

#### 标准venv
Python内置的虚拟环境工具
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# Windows: venv\Scripts\activate
```

**📺 可参考视频:** [虚拟环境搭建教程](https://youtu.be/myVgyitFzrA)

### 1.2 大模型相关配置

1. **GPT大模型使用方案**(第三方代理方式)
2. **非GPT大模型**(阿里通义千问、讯飞星火、智谱等大模型)使用方案(OneAPI方式)
3. **本地开源大模型使用方案**(Ollama方式)

**📺 可参考视频:** 
- [LLM集成解决方案](https://www.bilibili.com/video/BV12PCmYZEDt/?vd_source=30acb5331e4f5739ebbad50f7cc6b949)
- [YouTube版](https://youtu.be/CgZsdK43tcY)

---

## 2. 项目初始化

### 2.1 下载源码
GitHub或Gitee中下载工程文件到本地，下载地址如下：
- [GitHub](https://github.com/NanGePlus/AutoGenV04Test)
- [Gitee](https://gitee.com/NanGePlus/AutoGenV04Test)

### 2.2 构建项目
创建项目目录并初始化虚拟环境：

```bash
# 创建项目目录
mkdir AutoGenV04Test
cd AutoGenV04Test

# 使用uv创建虚拟环境（推荐）
uv venv
source .venv/bin/activate  # Linux/macOS
# Windows: .venv\Scripts\activate

# 或使用conda创建虚拟环境
# conda create -n autogen-env python=3.10
# conda activate autogen-env

# 或使用标准venv
# python -m venv venv
# source venv/bin/activate  # Linux/macOS
# Windows: venv\Scripts\activate
```

您可以使用任意代码编辑器（如VS Code、Sublime Text、Vim等）打开此项目目录进行开发。

### 2.3 将相关代码拷贝到项目工程中
直接将下载的文件夹中的文件拷贝到新建的项目目录中

### 2.4 安装项目依赖
您可以使用以下命令安装依赖包：

```bash
# 使用pip安装（标准方式）
pip install -U "autogen-agentchat"
pip install "autogen-ext[openai]"
pip install asyncio==3.4.3

# 或使用uv安装（速度更快）
uv pip install -U "autogen-agentchat"
uv pip install "autogen-ext[openai]"
uv pip install asyncio==3.4.3

# 或者一次性安装所有依赖（使用uv）
uv pip install -U "autogen-agentchat" "autogen-ext[openai]" asyncio==3.4.3
```

---

# 🧪 功能测试与演示

## 1. AgentChat框架基本功能测试
相关测试代码在`BasicTest`文件夹下

## 2. AutoGen Studio低代码平台使用

### 2.1 安装依赖
```bash
# 使用pip安装
pip install -U autogenstudio

# 或使用uv安装
uv pip install -U autogenstudio
```

### 2.2 启动服务
命令行终端启动服务，运行如下命令：
```bash
autogenstudio ui --port 8081
```

支持修改相关参数自定义应用程序如下:
- `--host <host>`: 指定主机地址，默认为localhost
- `--appdir <appdir>`: 指定存储应用程序文件（如数据库和生成的用户文件）的文件夹
- `--port <port>`: 指定端口号，默认为8080
- `--upgrade-database`: 升级数据库架构，默认为False
- `--reload`: 启用在对代码进行更改时自动重新加载服务器，默认为False
- `--database-uri`: 指定数据库URI

### 2.3 登录平台
访问 [http://localhost:8081/](http://localhost:8081/)

## 3. Magentic-One CLI使用

### 3.1 核心设计思想
<img src="./MagenticOneCli/01.png" alt="" width="600" />

### 3.2 工作流程
Magentic-One的工作基于一个多Agent架构，其中的首席协调者(Orchestrator)Agent负责高层次规划、指导其他Agent并跟踪任务进度。

协调者首先要制定一个处理任务的计划，在任务分类账中收集所需的事实和有根据的猜测。在计划的每一个步骤中，协调者都会创建一个进度账本，对任务进度进行自我反思，并检查任务是否已完成。

如果任务尚未完成，它会为Magentic-One的其他Agent分配子任务来完成。被分配的Agent完成子任务后，协调者会更新进度分类账，并以这种方式继续直至任务完成。

如果协调者发现进度不够，可以更新任务分类账并创建新计划。如上图所示，协调者的工作分为更新任务分类账的外循环和更新进度分类账的内循环。

### 3.3 命令行使用
```bash
# 首先安装依赖
pip install -U magentic-one-cli

# 设置环境变量（示例使用阿里云千问API）
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_API_KEY="你的API密钥"

# 直接运行问答
m1 "我今天的心情非常不错"
```

### 3.4 代码中集成使用
相关测试代码在`MagenticOneCli`文件夹下的`1_BasicTest.py`

## 4. AutoGen-Extensions 使用
相关测试代码在`Extensions`文件夹下

### 4.1 安装依赖
```bash
pip install autogen-ext
```

### 4.2 使用LangChain提供的Tools

#### 测试用例1: PythonAstREPLTool
测试脚本在`Extensions/LangChainTest`文件夹下
```bash
# 下载测试数据集
# https://github.com/pandas-dev/pandas/blob/main/doc/data/titanic.csv

# 安装依赖
pip install langchain_experimental

# 运行脚本
python PythonAstREPLTool.py
```

#### 测试用例2: DuckDuckGo搜索
```bash
# 安装依赖
pip install -qU duckduckgo-search langchain-community

# 运行脚本
python DuckDuckGoSearch.py
```

## 5. AutoGen版本更新功能测试

### 5.1 AutoGen V0.4.3更新
首先升级依赖包：
```bash
pip install --upgrade autogen-core
pip install --upgrade autogen-agentchat
pip install --upgrade autogen-ext
```

#### 使用缓存系统提高大模型的响应效率
使用缓存系统(DiskCacheStore和ChatCompletionCache)来避免重复的API请求，提高大模型的响应效率。第一次请求会从大模型获取响应并将其缓存，第二次请求相同消息时，将直接返回缓存的响应。

相关测试代码在`Extensions/Cache`目录下
```bash
# 安装依赖
pip install diskcache

# 在当前目录下创建空文件夹tmpdirname
mkdir -p tmpdirname

# 运行测试
python CacheTeam.py
```

#### 集成调用GraphRAG
```bash
# 安装依赖
pip install graphrag==1.2.0

# 创建项目并初始化
cd Extensions/GraphRAG
mkdir -p ./ragtest/input
cd ragtest
graphrag init --root ./

# 优化提示词(可选)
python -m graphrag prompt-tune --config ./settings.yaml --root ./ --language Chinese --output ./prompts

# 构建索引
graphrag index --root ./

# 检索测试
graphrag query --root ./ --method local --query "张三九的基本信息?"
graphrag query --root ./ --method global --query "给张三九一些健康建议?"

# AutoGen集成测试
python GraphRAGTeam.py
```

### 5.2 AutoGen V0.4.5更新
升级依赖包：
```bash
pip install --upgrade autogen-core
pip install --upgrade autogen-agentchat
pip install --upgrade autogen-ext
```

#### 为AgentChat的Agent和Team提供流式模型输出服务
相关测试代码在`BasicTest`目录下
```bash
python 5_RunTeamStream.py
```

#### 支持DeepSeek R1式推理输出
相关测试代码在`BasicTest`目录下
```bash
python 6_RunTeamDeepSeek.py
```

### 5.3 AutoGen V0.4.6更新
升级依赖包：
```bash
pip install --upgrade autogen-core
pip install --upgrade autogen-agentchat
pip install --upgrade autogen-ext
```

#### AutoGen与DeepSeek R1模型集成
相关测试代码在`BasicTest`目录下
```bash
python 7_RunTeamDeepSeekOllama.py
```

#### AutoGen与MCP服务器集成
```bash
# 安装依赖
pip install mcp-server-fetch
pip install json-schema-to-pydantic

# 运行测试
python 8_RunTeamStreamMCP.py
```

#### AutoGen与HTTP API工具集成
相关测试代码在`BasicTest`目录下
```bash
python 9_RunTeamStreamHttpTool.py
```

---

# 📊 最新版本功能更新总结

## AutoGen v0.5.3（2025年4月17日发布）
### 主要更新：
- **CodeExecutorAgent更新**：现在可以在同一次调用中生成和执行代码
- **AssistantAgent改进**：设置output_content_type时支持序列化
- **Team改进**：增加了可选参数emit_team_events
- **MCP改进**：mcp_server_tools工厂现在可以重用共享会话
- **Console改进**：在控制台中打印消息类型
- **Bug修复**：
  - 修复了Azure AI搜索工具客户端生命周期管理问题
  - 确保思考内容包含在移交上下文中

## AutoGen v0.5.2（2025年4月15日发布）
### 主要更新：
- **SocietyOfMindAgent消息处理改进**
- **新增模型支持**：添加了Gemini 2.5 Pro预览版
- **代码清理**：清理了AgentChat和Core中的冗余代码
- **Docker代码执行**：在执行后删除临时文件
- **终止条件修复**
- **更新依赖**：更新了json_schema_to_pydantic版本
- **暴露更多Task-Centric Memory参数**
- **修复**：
  - 修复Azure AI搜索嵌入问题
  - 为ChromaDB移除IncludeEnum的修复
  - 修复数据类的联合类型错误

## AutoGen v0.5.1（2025年4月3日发布）
### 主要更新：
- **AgentChat消息类型重大改进**：
  - 引入新的消息类型StructureMessage[T]
  - 支持应用程序定义的自定义消息类型
- **结构化输出增强**：
  - 模型客户端：使用json_output参数指定Pydantic模型
  - AssistantAgent：设置output_content_type自动生成结构化消息
- **Azure AI搜索工具**：新增工具允许Agent使用Azure AI搜索
- **SelectorGroupChat改进**：
  - 实现candidate_func参数过滤候选人池
  - 为selector_func和candidate_func添加异步支持
- **代码执行器改进**：
  - 为Docker执行器添加取消支持
  - 将start()和stop()作为CodeExecutor的接口方法
- **模型客户端改进**：
  - 改进相关文档和功能
  - 增强思考过程分析和推理功能

---

## 🎯 实战练习
课程包含多个实战练习，帮助学生掌握AutoGen框架：

1. 基础Agent创建与通信
2. Team团队协作系统设计
3. 工具集成与增强
4. 低代码平台AutoGen Studio使用
5. 命令行工具Magentic-One CLI应用
6. 知识图谱增强检索生成系统集成

---

## 🛣️ 学习路径
1. 完成环境配置
2. 学习框架基础概念
3. 完成基础练习
4. 尝试扩展功能集成
5. 设计并实现自己的多智能体系统

---

## 📚 参考资源
- AutoGen官方文档：[https://microsoft.github.io/autogen/stable/index.html](https://microsoft.github.io/autogen/stable/index.html)
- AutoGen GitHub仓库：[https://github.com/microsoft/autogen](https://github.com/microsoft/autogen)
- 课程示例代码仓库：[https://github.com/NanGePlus/AutoGenV04Test](https://github.com/NanGePlus/AutoGenV04Test)

---





