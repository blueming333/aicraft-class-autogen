# GitHub官方MCP服务器集成指南

本文档提供了关于如何安装和配置GitHub官方MCP服务器与AutoGen框架集成的详细说明。

## 1. 概述

GitHub官方MCP服务器是GitHub官方提供的一个Go实现的MCP协议服务器，它提供了全面的GitHub API访问能力，包括但不限于：

- 搜索代码、存储库、问题和用户
- 获取文件内容和存储库信息
- 创建和更新文件
- 列出和获取分支信息
- 创建和管理Pull Request
- 查看提交历史和提交详情
- 代码扫描安全警报处理

与Python版本的MCP服务器相比，官方版本提供了更全面的功能支持和更好的性能。

## 2. 安装GitHub官方MCP服务器

### 安装Go环境

首先，需要确保你的系统上安装了Go语言环境。GitHub官方MCP服务器是用Go语言开发的。

1. 下载并安装Go：https://golang.org/dl/
2. 验证安装：
   ```bash
   go version
   ```

### 安装GitHub MCP服务器

使用Go的包管理工具安装GitHub官方MCP服务器：

```bash
go install github.com/github/github-mcp-server/cmd/mcp-server-github@latest
```

安装完成后，可以验证是否安装成功：

```bash
which mcp-server-github
```

如果显示了安装路径，则表示安装成功。

## 3. 配置环境变量

GitHub官方MCP服务器需要GitHub API令牌才能访问GitHub服务。请确保设置以下环境变量：

```bash
# 在你的.env文件中添加
GITHUB_TOKEN=your_github_personal_access_token
```

您可以在GitHub的[Personal Access Tokens页面](https://github.com/settings/tokens)创建一个具有适当权限的令牌。对于大多数操作，建议至少包含以下权限：

- `repo` - 完整的存储库访问权限
- `read:org` - 读取组织成员资格
- `read:user` - 读取用户信息

## 4. 在AutoGen中使用GitHub官方MCP服务器

我们提供了一个完整的示例代码`GitHubOfficialMcpExample.py`，展示了如何在AutoGen框架中集成GitHub官方MCP服务器。

### 关键代码解析

```python
# 配置GitHub官方MCP服务器
import subprocess
result = subprocess.run(["which", "mcp-server-github"], capture_output=True, text=True)
github_mcp_path = result.stdout.strip()

# 创建MCP服务器参数
env = os.environ.copy()  # 复制当前环境变量
github_mcp_server = StdioServerParams(
    command=github_mcp_path,  # 使用GitHub官方MCP服务器路径
    args=[],                  # GitHub官方MCP服务器不需要额外参数
    env=env                   # 传递环境变量，包括GITHUB_TOKEN
)

# 获取MCP工具
tools = await mcp_server_tools(github_mcp_server)
```

### 运行示例代码

执行以下命令运行示例：

```bash
python GitHubOfficialMcpExample.py
```

运行后，程序会：
1. 检查是否安装了GitHub MCP服务器
2. 启动服务器并加载可用工具
3. 显示可用的示例任务列表
4. 让用户选择要执行的任务
5. 执行选定的任务并显示结果

## 5. GitHub官方MCP服务器支持的主要工具

根据GitHub官方文档，以下是一些关键工具的使用说明：

### 搜索存储库
```json
{
  "query": "tensorflow language:python stars:>1000",
  "sort": "stars",
  "order": "desc",
  "page": 1,
  "perPage": 5
}
```

### 搜索代码
```json
{
  "query": "function filename:*.js",
  "sort": "best-match",
  "order": "desc",
  "page": 1,
  "perPage": 5
}
```

### 获取文件内容
```json
{
  "owner": "github",
  "repo": "github-mcp-server",
  "path": "README.md",
  "ref": "main"
}
```

### 列出提交记录
```json
{
  "owner": "github",
  "repo": "github-mcp-server",
  "sha": "main",
  "page": 1,
  "perPage": 5
}
```

## 6. 注意事项

- GitHub API有请求速率限制，未验证的请求限制为每小时60次，验证请求限制为每小时5000次
- 提交包含敏感信息的请求时要小心，避免泄露密钥或个人信息
- 建议对生产环境中的GitHub令牌设置适当的权限范围，遵循最小权限原则

## 7. 故障排除

如果遇到问题，可以尝试以下解决方案：

- 确保GITHUB_TOKEN环境变量已正确设置并有足够的权限
- 检查网络连接，确保可以访问GitHub API
- 查看是否达到了GitHub API的速率限制
- 检查Go和GitHub MCP服务器的安装是否正确

## 8. 资源链接

- [GitHub官方MCP服务器](https://github.com/github/github-mcp-server)
- [GitHub REST API文档](https://docs.github.com/en/rest)
- [AutoGen文档](https://microsoft.github.io/autogen/) 