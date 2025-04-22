from typing import Annotated, Tuple
from urllib.parse import urlparse, urlunparse

import markdownify
import readabilipy.simple_json
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
from protego import Protego
from pydantic import BaseModel, Field, AnyUrl

# 定义默认的用户代理字符串，用于自动抓取模式
DEFAULT_USER_AGENT_AUTONOMOUS = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"
# 定义默认的用户代理字符串，用于手动抓取模式
DEFAULT_USER_AGENT_MANUAL = "ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)"


def extract_content_from_html(html: str) -> str:
    """从HTML中提取内容并转换为Markdown格式。
    
    Args:
        html: 需要处理的原始HTML内容
        
    Returns:
        简化后的markdown版本内容
    """
    ret = readabilipy.simple_json.simple_json_from_html_string(
        html, use_readability=True
    )
    if not ret["content"]:
        return "<error>Page failed to be simplified from HTML</error>"
    content = markdownify.markdownify(
        ret["content"],
        heading_style=markdownify.ATX,
    )
    return content


def get_robots_txt_url(url: str) -> str:
    """获取网站的robots.txt文件URL。
    
    Args:
        url: 网站URL
        
    Returns:
        robots.txt文件的URL
    """
    # 解析URL组件
    parsed = urlparse(url)

    # 重构基础URL，只包含scheme, netloc和/robots.txt路径
    robots_url = urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))

    return robots_url


async def check_may_autonomously_fetch_url(url: str, user_agent: str) -> None:
    """
    检查URL是否可以根据robots.txt规则被用户代理抓取。
    如果不允许，则抛出McpError异常。
    
    Args:
        url: 要检查的URL
        user_agent: 用户代理字符串
    """
    from httpx import AsyncClient, HTTPError

    # 获取robots.txt文件的URL
    robot_txt_url = get_robots_txt_url(url)

    async with AsyncClient() as client:
        try:
            response = await client.get(
                robot_txt_url,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
            )
        except HTTPError:
            raise McpError(
                INTERNAL_ERROR,
                f"Failed to fetch robots.txt {robot_txt_url} due to a connection issue",
            )
        if response.status_code in (401, 403):
            raise McpError(
                INTERNAL_ERROR,
                f"When fetching robots.txt ({robot_txt_url}), received status {response.status_code} so assuming that autonomous fetching is not allowed, the user can try manually fetching by using the fetch prompt",
            )
        elif 400 <= response.status_code < 500:
            return
        robot_txt = response.text
    # 处理robots.txt内容，移除注释行
    processed_robot_txt = "\n".join(
        line for line in robot_txt.splitlines() if not line.strip().startswith("#")
    )
    # 使用Protego解析robots.txt
    robot_parser = Protego.parse(processed_robot_txt)
    # 检查是否允许抓取
    if not robot_parser.can_fetch(str(url), user_agent):
        raise McpError(
            INTERNAL_ERROR,
            f"The sites robots.txt ({robot_txt_url}), specifies that autonomous fetching of this page is not allowed, "
            f"<useragent>{user_agent}</useragent>\n"
            f"<url>{url}</url>"
            f"<robots>\n{robot_txt}\n</robots>\n"
            f"The assistant must let the user know that it failed to view the page. The assistant may provide further guidance based on the above information.\n"
            f"The assistant can tell the user that they can try manually fetching the page by using the fetch prompt within their UI.",
        )


async def fetch_url(
    url: str, user_agent: str, force_raw: bool = False
) -> Tuple[str, str]:
    """
    抓取URL并返回准备好供LLM使用的内容，以及包含状态信息的前缀字符串。
    
    Args:
        url: 要抓取的URL
        user_agent: 用户代理字符串
        force_raw: 是否强制返回原始HTML内容而不进行简化
        
    Returns:
        包含内容和前缀的元组
    """
    from httpx import AsyncClient, HTTPError

    async with AsyncClient() as client:
        try:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
                timeout=30,
            )
        except HTTPError as e:
            raise McpError(INTERNAL_ERROR, f"Failed to fetch {url}: {e!r}")
        if response.status_code >= 400:
            raise McpError(
                INTERNAL_ERROR,
                f"Failed to fetch {url} - status code {response.status_code}",
            )

        page_raw = response.text

    # 检查内容类型，判断是否为HTML
    content_type = response.headers.get("content-type", "")
    is_page_html = (
        "<html" in page_raw[:100] or "text/html" in content_type or not content_type
    )

    # 对HTML内容进行简化处理，除非强制要求原始内容
    if is_page_html and not force_raw:
        return extract_content_from_html(page_raw), ""

    return (
        page_raw,
        f"Content type {content_type} cannot be simplified to markdown, but here is the raw content:\n",
    )


class Fetch(BaseModel):
    """抓取URL的参数类。"""

    url: Annotated[AnyUrl, Field(description="URL to fetch")]
    max_length: Annotated[
        int,
        Field(
            default=5000,
            description="Maximum number of characters to return.",
            gt=0,
            lt=1000000,
        ),
    ]
    start_index: Annotated[
        int,
        Field(
            default=0,
            description="On return output starting at this character index, useful if a previous fetch was truncated and more context is required.",
            ge=0,
        ),
    ]
    raw: Annotated[
        bool,
        Field(
            default=False,
            description="Get the actual HTML content if the requested page, without simplification.",
        ),
    ]


async def serve(
    custom_user_agent: str | None = None, ignore_robots_txt: bool = False
) -> None:
    """运行fetch MCP服务器。
    
    Args:
        custom_user_agent: 可选的自定义User-Agent字符串
        ignore_robots_txt: 是否忽略robots.txt限制
    """
    # 创建MCP服务器实例
    server = Server("mcp-fetch")
    user_agent_autonomous = custom_user_agent or DEFAULT_USER_AGENT_AUTONOMOUS
    user_agent_manual = custom_user_agent or DEFAULT_USER_AGENT_MANUAL

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """定义并返回工具列表"""
        return [
            Tool(
                name="fetch",
                description="""Fetches a URL from the internet and optionally extracts its contents as markdown.

Although originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access. Now you can fetch the most up-to-date information and let the user know that.""",
                inputSchema=Fetch.model_json_schema(),
            )
        ]

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """定义并返回提示列表"""
        return [
            Prompt(
                name="fetch",
                description="Fetch a URL and extract its contents as markdown",
                arguments=[
                    PromptArgument(
                        name="url", description="URL to fetch", required=True
                    )
                ],
            )
        ]

    @server.call_tool()
    async def call_tool(name, arguments: dict) -> list[TextContent]:
        """处理工具调用请求"""
        try:
            # 验证参数
            args = Fetch(**arguments)
        except ValueError as e:
            raise McpError(INVALID_PARAMS, str(e))

        url = str(args.url)
        if not url:
            raise McpError(INVALID_PARAMS, "URL is required")

        # 检查robots.txt限制（除非忽略）
        if not ignore_robots_txt:
            await check_may_autonomously_fetch_url(url, user_agent_autonomous)

        # 抓取URL内容
        content, prefix = await fetch_url(
            url, user_agent_autonomous, force_raw=args.raw
        )
        # 处理长内容截断
        if len(content) > args.max_length:
            content = content[args.start_index : args.start_index + args.max_length]
            content += f"\n\n<error>Content truncated. Call the fetch tool with a start_index of {args.start_index + args.max_length} to get more content.</error>"
        return [TextContent(type="text", text=f"{prefix}Contents of {url}:\n{content}")]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        """处理提示获取请求"""
        if not arguments or "url" not in arguments:
            raise McpError(INVALID_PARAMS, "URL is required")

        url = arguments["url"]

        try:
            # 抓取URL内容
            content, prefix = await fetch_url(url, user_agent_manual)
            # TODO: after SDK bug is addressed, don't catch the exception
        except McpError as e:
            return GetPromptResult(
                description=f"Failed to fetch {url}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=str(e)),
                    )
                ],
            )
        return GetPromptResult(
            description=f"Contents of {url}",
            messages=[
                PromptMessage(
                    role="user", content=TextContent(type="text", text=prefix + content)
                )
            ],
        )

    # 创建初始化选项并启动服务器
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


# from .server import serve


def main():
    """MCP Fetch Server - 为MCP提供HTTP抓取功能的主入口"""
    import argparse
    import asyncio

    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="give a model the ability to make web requests"
    )
    parser.add_argument("--user-agent", type=str, help="Custom User-Agent string")
    parser.add_argument(
        "--ignore-robots-txt",
        action="store_true",
        help="Ignore robots.txt restrictions",
    )

    # 启动服务器
    args = parser.parse_args()
    asyncio.run(serve(args.user_agent, args.ignore_robots_txt))


if __name__ == "__main__":
    main()