"""
PostgreSQL工具模块 - 提供PostgreSQL数据库访问工具
"""

import os
import logging
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools


# 配置日志
logger = logging.getLogger(__name__)

async def create_postgres_tools(timeout=30):
    """
    创建PostgreSQL MCP工具
    
    参数:
        timeout: 连接超时时间(秒)
    返回:
        PostgreSQL MCP工具列表
    """
    try:
        # 设置环境变量传递给子进程
        env = os.environ.copy()
        
        # 创建SSE服务器参数
        postgres_mcp_server = SseServerParams(url="http://113.45.249.18:37696/mcp/sse")
        
        # 获取MCP工具
        logger.info("正在连接PostgreSQL MCP服务器...")
        tools = await mcp_server_tools(postgres_mcp_server)
        logger.info(f"成功加载PostgreSQL MCP工具: {len(tools)} 个工具可用")
        return tools
    except Exception as e:
        logger.error(f"加载PostgreSQL MCP工具失败: {e}")
        return []

