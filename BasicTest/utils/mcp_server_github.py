from typing import Annotated, Tuple, List, Dict, Any, Optional
from urllib.parse import urlparse
import json
import os
import sys
import re
import base64
import time
import asyncio
import httpx
from datetime import datetime
from enum import Enum

from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field, validator, root_validator

# 定义默认的用户代理
DEFAULT_USER_AGENT = "ModelContextProtocol/1.0 (GitHub; +https://github.com/modelcontextprotocol/servers)"

# GitHub API基础URL
GITHUB_API_BASE_URL = "https://api.github.com"

# 最大显示结果数量
MAX_RESULTS = 5
MAX_FILE_SIZE = 100000  # 最大文件大小，约100KB
REQUEST_TIMEOUT = 30  # 请求超时时间(秒)


class RepositoryInfo(BaseModel):
    """存储库信息参数"""
    owner: Annotated[str, Field(description="存储库所有者")]
    repo: Annotated[str, Field(description="存储库名称")]


class FileContent(BaseModel):
    """文件内容参数"""
    path: Annotated[str, Field(description="文件路径")]
    content: Annotated[str, Field(description="文件内容")]


class RepoContent(RepositoryInfo):
    """获取存储库文件内容的参数"""
    path: Annotated[Optional[str], Field(description="文件或目录路径", default=None)]
    ref: Annotated[Optional[str], Field(description="Git引用（分支、标签或提交SHA）", default=None)]


class SearchRepo(BaseModel):
    """搜索存储库的参数"""
    query: Annotated[str, Field(description="搜索查询字符串")]
    sort: Annotated[Optional[str], Field(description="排序字段", default=None)]
    order: Annotated[Optional[str], Field(description="排序顺序 (asc或desc)", default=None)]
    page: Annotated[Optional[int], Field(description="页码", default=1)]
    per_page: Annotated[Optional[int], Field(description="每页结果数", default=30)]


class SearchCode(BaseModel):
    """搜索代码的参数"""
    query: Annotated[str, Field(description="搜索查询字符串")]
    sort: Annotated[Optional[str], Field(description="排序字段", default=None)]
    order: Annotated[Optional[str], Field(description="排序顺序 (asc或desc)", default=None)]
    page: Annotated[Optional[int], Field(description="页码", default=1)]
    per_page: Annotated[Optional[int], Field(description="每页结果数", default=30)]


class ListBranches(RepositoryInfo):
    """列出分支的参数"""
    page: Annotated[Optional[int], Field(description="页码", default=1)]
    per_page: Annotated[Optional[int], Field(description="每页结果数", default=30)]


class ListCommits(RepositoryInfo):
    """列出提交的参数"""
    sha: Annotated[Optional[str], Field(description="分支名称、标签或提交SHA", default=None)]
    path: Annotated[Optional[str], Field(description="仅包含此文件路径的提交", default=None)]
    page: Annotated[Optional[int], Field(description="页码", default=1)]
    per_page: Annotated[Optional[int], Field(description="每页结果数", default=30)]


class GetCommit(RepositoryInfo):
    """获取提交详情的参数"""
    sha: Annotated[str, Field(description="提交SHA、分支名称或标签名称")]
    page: Annotated[Optional[int], Field(description="页码", default=1)]
    per_page: Annotated[Optional[int], Field(description="每页结果数", default=30)]


class CreateOrUpdateFile(RepositoryInfo):
    """创建或更新文件的参数"""
    path: Annotated[str, Field(description="文件路径")]
    message: Annotated[str, Field(description="提交消息")]
    content: Annotated[str, Field(description="文件内容")]
    branch: Annotated[Optional[str], Field(description="分支名称", default=None)]
    sha: Annotated[Optional[str], Field(description="更新时的文件SHA", default=None)]


class RepoInfo(BaseModel):
    """存储库信息模型"""
    name: str
    owner: Any  # 修改为Any类型，因为有时是字符串，有时是字典
    full_name: str = ""
    description: Optional[str] = None
    html_url: str
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    license: Optional[Dict[str, str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    language: Optional[str] = None
    
    @validator('full_name', pre=True, always=True)
    def set_full_name(cls, v, values):
        if not v and 'owner' in values and 'name' in values:
            if isinstance(values['owner'], dict) and 'login' in values['owner']:
                return f"{values['owner']['login']}/{values['name']}"
            else:
                return f"{values['owner']}/{values['name']}"
        return v
        
    @validator('owner', pre=True)
    def process_owner(cls, v):
        """处理owner字段，若为字典则提取login值"""
        if isinstance(v, dict) and 'login' in v:
            return v['login']
        return v


class SearchType(str, Enum):
    """搜索类型枚举"""
    REPOS = "repositories"
    CODE = "code"
    ISSUES = "issues"
    USERS = "users"


class SearchParams(BaseModel):
    """搜索参数模型"""
    query: str
    type: SearchType = SearchType.CODE
    per_page: int = Field(default=MAX_RESULTS, le=100)
    page: int = 1


class GitHubClient:
    """GitHub API客户端"""
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """初始化GitHub客户端
        
        Args:
            token: GitHub API令牌（可选）
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-MCP-Client/1.0",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    async def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, json_data: Dict = None) -> Dict:
        """发送API请求
        
        Args:
            endpoint: API端点
            method: HTTP方法
            params: URL参数
            json_data: JSON数据体
            
        Returns:
            Dict: API响应
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                if method == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=self.headers, params=params, json=json_data)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()  # 会抛出HTTPStatusError
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"未找到资源: {url}")
            elif e.response.status_code == 403 and "rate limit exceeded" in e.response.text.lower():
                raise ValueError("GitHub API速率限制已达到，请稍后再试或提供有效的API令牌")
            else:
                raise ValueError(f"GitHub API请求失败: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"请求错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"请求处理错误: {str(e)}")
    
    async def get_repo(self, owner: str, repo: str) -> RepoInfo:
        """获取存储库信息
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            
        Returns:
            RepoInfo: 存储库信息
        """
        endpoint = f"/repos/{owner}/{repo}"
        data = await self._make_request(endpoint)
        return RepoInfo(**data)
    
    async def get_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> FileContent:
        """获取文件内容
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            path: 文件路径
            ref: 分支或提交SHA (可选)
            
        Returns:
            FileContent: 文件内容
        """
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref} if ref else {}
        data = await self._make_request(endpoint, params=params)
        
        file_content = FileContent(**data)
        
        # 解码Base64编码的内容
        if file_content.content and file_content.encoding == "base64":
            try:
                content = base64.b64decode(file_content.content.replace("\n", "")).decode("utf-8")
                file_content.content = content
            except UnicodeDecodeError:
                file_content.content = "[二进制内容，无法显示]"
        
        return file_content
    
    async def list_directory(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> List[FileContent]:
        """列出目录内容
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            path: 目录路径
            ref: 分支或提交SHA (可选)
            
        Returns:
            List[FileContent]: 目录内容列表
        """
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref} if ref else {}
        data = await self._make_request(endpoint, params=params)
        
        if not isinstance(data, list):
            raise ValueError(f"路径 '{path}' 不是目录")
            
        return [FileContent(**item) for item in data]
    
    async def search(self, search_params: SearchParams) -> Dict:
        """搜索GitHub
        
        Args:
            search_params: 搜索参数
            
        Returns:
            Dict: 搜索结果
        """
        endpoint = f"/search/{search_params.type.value}"
        params = {
            "q": search_params.query,
            "per_page": search_params.per_page,
            "page": search_params.page,
        }
        return await self._make_request(endpoint, params=params)
    
    async def list_branches(self, owner: str, repo: str) -> List[Dict]:
        """列出存储库分支
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            
        Returns:
            List[Dict]: 分支列表
        """
        endpoint = f"/repos/{owner}/{repo}/branches"
        return await self._make_request(endpoint)
    
    async def get_branch(self, owner: str, repo: str, branch: str) -> Dict:
        """获取分支信息
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            branch: 分支名称
            
        Returns:
            Dict: 分支信息
        """
        endpoint = f"/repos/{owner}/{repo}/branches/{branch}"
        return await self._make_request(endpoint)
    
    async def list_releases(self, owner: str, repo: str) -> List[Dict]:
        """列出存储库发布版本
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            
        Returns:
            List[Dict]: 发布版本列表
        """
        endpoint = f"/repos/{owner}/{repo}/releases"
        return await self._make_request(endpoint)
    
    async def get_readme(self, owner: str, repo: str, ref: Optional[str] = None) -> FileContent:
        """获取README文件
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            ref: 分支或提交SHA (可选)
            
        Returns:
            FileContent: README文件内容
        """
        endpoint = f"/repos/{owner}/{repo}/readme"
        params = {"ref": ref} if ref else {}
        data = await self._make_request(endpoint, params=params)
        
        file_content = FileContent(**data)
        
        # 解码Base64编码的内容
        if file_content.content and file_content.encoding == "base64":
            try:
                content = base64.b64decode(file_content.content.replace("\n", "")).decode("utf-8")
                file_content.content = content
            except UnicodeDecodeError:
                file_content.content = "[二进制内容，无法显示]"
        
        return file_content
    
    async def list_issues(self, owner: str, repo: str, state: str = "open", labels: Optional[str] = None, per_page: int = 30) -> List[Dict]:
        """列出存储库问题
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            state: 问题状态 ("open", "closed", "all")
            labels: 标签
            per_page: 每页数量
            
        Returns:
            List[Dict]: 问题列表
        """
        endpoint = f"/repos/{owner}/{repo}/issues"
        params = {
            "state": state,
            "per_page": min(per_page, 100)
        }
        if labels:
            params["labels"] = labels
            
        return await self._make_request(endpoint, params=params)
    
    async def compare_commits(self, owner: str, repo: str, base: str, head: str) -> Dict:
        """比较两个提交
        
        Args:
            owner: 存储库所有者
            repo: 存储库名称
            base: 基础提交或分支
            head: 目标提交或分支
            
        Returns:
            Dict: 比较结果
        """
        endpoint = f"/repos/{owner}/{repo}/compare/{base}...{head}"
        return await self._make_request(endpoint)


async def github_api_request(endpoint: str, method: str = "GET", params: dict = None, headers: dict = None, data: dict = None) -> Dict[str, Any]:
    """
    发送请求到GitHub API
    
    Args:
        endpoint: API端点
        method: HTTP方法
        params: URL参数
        headers: HTTP头
        data: 请求体数据
        
    Returns:
        API响应数据
    """
    from httpx import AsyncClient, HTTPError
    
    url = f"{GITHUB_API_BASE_URL}{endpoint}"
    default_headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": DEFAULT_USER_AGENT
    }
    
    # 添加GitHub令牌（如果可用）
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        default_headers["Authorization"] = f"token {github_token}"
    
    # 合并自定义头
    if headers:
        default_headers.update(headers)
    
    async with AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, params=params, headers=default_headers, timeout=30)
            elif method == "POST":
                response = await client.post(url, json=data, params=params, headers=default_headers, timeout=30)
            elif method == "PUT":
                response = await client.put(url, json=data, params=params, headers=default_headers, timeout=30)
            elif method == "DELETE":
                response = await client.delete(url, params=params, headers=default_headers, timeout=30)
            elif method == "PATCH":
                response = await client.patch(url, json=data, params=params, headers=default_headers, timeout=30)
            else:
                raise McpError(INTERNAL_ERROR, f"不支持的HTTP方法: {method}")
                
            response.raise_for_status()
            return response.json() if response.text else {}
            
        except HTTPError as e:
            error_message = f"GitHub API请求失败: {e!r}"
            if e.response and e.response.text:
                try:
                    error_data = e.response.json()
                    if "message" in error_data:
                        error_message = f"GitHub API错误: {error_data['message']}"
                except:
                    error_message = f"GitHub API错误: {e.response.text}"
            raise McpError(INTERNAL_ERROR, error_message)


async def serve() -> None:
    """启动Github MCP服务"""
    # 创建GitHubClient实例
    client = GitHubClient()
    
    # 创建MCP服务器
    server = Server("GitHub MCP服务")
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """定义并返回工具列表"""
        return [
            Tool(
                name="get_repo",
                description="获取GitHub存储库信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "存储库所有者"},
                        "repo": {"type": "string", "description": "存储库名称"}
                    },
                    "required": ["owner", "repo"]
                }
            ),
            Tool(
                name="get_file_content",
                description="获取GitHub存储库中的文件内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "存储库所有者"},
                        "repo": {"type": "string", "description": "存储库名称"},
                        "path": {"type": "string", "description": "文件路径"},
                        "ref": {"type": "string", "description": "分支或提交SHA"}
                    },
                    "required": ["owner", "repo", "path"]
                }
            ),
            Tool(
                name="list_directory",
                description="列出GitHub存储库中的目录内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "存储库所有者"},
                        "repo": {"type": "string", "description": "存储库名称"},
                        "path": {"type": "string", "description": "目录路径，使用空字符串表示根目录"},
                        "ref": {"type": "string", "description": "分支或提交SHA"}
                    },
                    "required": ["owner", "repo", "path"]
                }
            ),
            Tool(
                name="github_search",
                description="搜索GitHub内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_params": {
                            "type": "object",
                            "description": "搜索参数"
                        }
                    },
                    "required": ["search_params"]
                }
            ),
            Tool(
                name="list_branches",
                description="列出GitHub存储库的分支",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "存储库所有者"},
                        "repo": {"type": "string", "description": "存储库名称"}
                    },
                    "required": ["owner", "repo"]
                }
            ),
            Tool(
                name="get_readme",
                description="获取GitHub存储库的README文件",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "owner": {"type": "string", "description": "存储库所有者"},
                        "repo": {"type": "string", "description": "存储库名称"},
                        "ref": {"type": "string", "description": "分支或提交SHA"}
                    },
                    "required": ["owner", "repo"]
                }
            ),
            Tool(
                name="list_commits",
                description="获取GitHub存储库的提交记录",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "owner": {"type": "string", "description": "存储库所有者"},
                        "repo": {"type": "string", "description": "存储库名称"},
                        "sha": {"type": "string", "description": "分支名称、标签或提交SHA"},
                        "path": {"type": "string", "description": "仅包含此文件路径的提交"},
                        "per_page": {"type": "integer", "description": "每页结果数，最大30"},
                        "page": {"type": "integer", "description": "页码，从1开始"}
                    },
                    "required": ["owner", "repo"]
                }
            ),
            Tool(
                name="get_commit",
                description="获取GitHub存储库的特定提交详情",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "owner": {"type": "string", "description": "存储库所有者"},
                        "repo": {"type": "string", "description": "存储库名称"},
                        "sha": {"type": "string", "description": "提交SHA"}
                    },
                    "required": ["owner", "repo", "sha"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """处理工具调用请求"""
        try:
            if name == "get_repo":
                try:
                    result = await client.get_repo(**arguments)
                    return [TextContent(type="text", text=f"""
## 存储库信息: {result.full_name}

- 描述: {result.description or '无描述'}
- URL: {result.html_url}
- 星标数: {result.stargazers_count}
- Fork数: {result.forks_count}
- 开放问题: {result.open_issues_count}
- 主要语言: {result.language or '未指定'}
- 许可证: {result.license.get('name') if result.license else '未指定'}
- 创建于: {result.created_at}
- 最后更新: {result.updated_at}
""")]
                except Exception as e:
                    return [TextContent(type="text", text=f"获取存储库信息失败: {str(e)}")]
            
            elif name == "get_file_content":
                try:
                    result = await client.get_file_content(**arguments)
                    return [TextContent(
                        type="text", 
                        text=f"```{result.name.split('.')[-1] if '.' in result.name else 'txt'}\n{result.content}\n```"
                    )]
                except Exception as e:
                    return [TextContent(type="text", text=f"获取文件内容失败: {str(e)}")]
            
            elif name == "list_directory":
                try:
                    result = await client.list_directory(**arguments)
                    return [TextContent(
                        type="text",
                        text="| 名称 | 类型 | 大小 | URL |\n| --- | --- | --- | --- |\n" + 
                             "".join([f"| {item.name} | {item.type} | {item.size} bytes | {item.html_url} |\n" for item in result])
                    )]
                except Exception as e:
                    return [TextContent(type="text", text=f"列出目录内容失败: {str(e)}")]
            
            elif name == "github_search":
                try:
                    search_params = SearchParams(**arguments.get("search_params", {}))
                    result = await client.search(search_params)
                    return [TextContent(type="text", text=f"""
## 搜索结果

总计找到: {result.get('total_count', 0)} 个结果
展示前 {min(MAX_RESULTS, len(result.get('items', [])))} 个结果:

{
''.join([f"""
### {i+1}. {item.get('name', '')} {'('+item.get('repository', {}).get('full_name', '')+')' if 'repository' in item else ''}
{'- '+item.get('description', '') if item.get('description') else ''}
- URL: {item.get('html_url', '')}
{
  ('- 文件路径: '+item.get('path', '')) if 'path' in item else 
  ('- 星标数: '+str(item.get('stargazers_count', 0))) if 'stargazers_count' in item else ''
}
""" for i, item in enumerate(result.get('items', [])[:MAX_RESULTS])])
}

注意: 只显示前 {min(MAX_RESULTS, len(result.get('items', [])))} 个结果。
""")]
                except Exception as e:
                    return [TextContent(type="text", text=f"搜索GitHub内容失败: {str(e)}")]
            
            elif name == "list_branches":
                try:
                    result = await client.list_branches(**arguments)
                    return [TextContent(
                        type="text",
                        text="| 分支名 | SHA | 保护状态 |\n| --- | --- | --- |\n" + 
                             "".join([f"| {branch.get('name', '')} | {branch.get('commit', {}).get('sha', '')[:7] if branch.get('commit') else ''} | {'是' if branch.get('protected', False) else '否'} |\n" 
                                     for branch in result])
                    )]
                except Exception as e:
                    return [TextContent(type="text", text=f"列出分支失败: {str(e)}")]
            
            elif name == "get_readme":
                try:
                    result = await client.get_readme(**arguments)
                    return [TextContent(type="text", text=result.content)]
                except Exception as e:
                    return [TextContent(type="text", text=f"获取README失败: {str(e)}")]
            
            elif name == "list_commits":
                try:
                    result = await client.list_commits(**arguments)
                    return [TextContent(
                        type="text",
                        text="| 提交SHA | 提交信息 | 作者和日期 |\n| --- | --- | --- |\n" + 
                             "".join([f"| {commit.get('sha', '')[:7]} | {commit.get('commit', {}).get('message', '')[:50].replace('|', '\\|')} | {commit.get('commit', {}).get('author', {}).get('name', '')} 在 {commit.get('commit', {}).get('author', {}).get('date', '')[:10]} |\n" 
                                     for commit in result])
                    )]
                except Exception as e:
                    return [TextContent(type="text", text=f"获取提交记录失败: {str(e)}")]
            
            elif name == "get_commit":
                try:
                    result = await client.get_commit(**arguments)
                    
                    # 提取提交文件信息
                    files_info = ""
                    if "files" in result and result["files"]:
                        files_info = "\n### 更改文件:\n"
                        for file in result["files"]:
                            files_info += f"- {file.get('filename', '')}: +{file.get('additions', 0)} -{file.get('deletions', 0)}\n"
                    
                    return [TextContent(type="text", text=f"""
## 提交详情

- 提交SHA: {result.get('sha', '')}
- 提交信息: {result.get('commit', {}).get('message', '')}
- 作者: {result.get('commit', {}).get('author', {}).get('name', '')}
- 日期: {result.get('commit', {}).get('author', {}).get('date', '')}
- 提交URL: {result.get('html_url', '')}
{files_info}
""")]
                except Exception as e:
                    return [TextContent(type="text", text=f"获取提交详情失败: {str(e)}")]
            
            else:
                return [TextContent(type="text", text=f"未知工具: {name}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"工具调用失败: {str(e)}")]

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """定义并返回提示列表"""
        return [
            Prompt(
                name="github_tools",
                description="""
# GitHub工具

这些工具允许你操作GitHub的存储库、文件和其他资源。

## 主要功能:

1. **获取存储库信息** - 获取存储库的详细信息，包括星标数、Fork数、问题数等
2. **获取文件内容** - 获取存储库中的文件内容
3. **列出目录内容** - 查看存储库中某个目录的内容
4. **搜索GitHub** - 使用github_search工具搜索存储库、代码、问题或用户
5. **列出分支** - 获取存储库的所有分支
6. **获取README** - 获取存储库的README文件
7. **列出提交** - 获取存储库的提交历史记录
8. **获取提交详情** - 查看特定提交的详细信息

## 使用提示:

- 搜索时可以使用GitHub的高级搜索语法，如`language:python stars:>100`
- 在获取文件内容时，如果文件过大，可能只会返回部分内容
- 查看提交历史时可以指定分支名或路径过滤
                """,
                arguments=[]
            )
        ]
    
    # 启动服务器
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


def main():
    """GitHub MCP服务器 - 为MCP提供GitHub访问功能的主入口"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="为模型提供GitHub访问能力"
    )
    
    args = parser.parse_args()
    asyncio.run(serve())


if __name__ == "__main__":
    main() 