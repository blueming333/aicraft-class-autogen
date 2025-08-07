#!/usr/bin/env python3
"""
测试本地MySQL工具
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../..')
sys.path.append(project_root)

from AiCraftTest.mcptools.mysql_tools import create_mysql_tools, QueryInput, TablesInput, TableSchemaInput
from autogen_core import CancellationToken

async def test_mysql_tools_detailed():
    """详细测试MySQL工具功能"""
    print("=== 详细测试MySQL工具 ===\n")
    
    # 1. 创建工具
    print("1. 创建MySQL工具:")
    tools = create_mysql_tools()
    
    if not tools:
        print("❌ 工具创建失败")
        return False
    
    print(f"✅ 成功创建 {len(tools)} 个MySQL工具:")
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool.name}: {tool.description}")
    
    # 获取各个工具
    query_tool = None
    list_tables_tool = None
    describe_table_tool = None
    
    for tool in tools:
        if tool.name == "query":
            query_tool = tool
        elif tool.name == "list_tables":
            list_tables_tool = tool
        elif tool.name == "describe_table":
            describe_table_tool = tool
    
    # 2. 测试列表表（连接已在工具创建时自动建立）
    print("\n2. 测试获取表列表:")
    if list_tables_tool:
        result = await list_tables_tool.run(TablesInput(), CancellationToken())
        print(result)
    else:
        print("❌ 列表表工具未找到")
        return False
    
    # 3. 测试表结构
    print("\n3. 测试获取表结构 (users表):")
    if describe_table_tool:
        result = await describe_table_tool.run(TableSchemaInput(table="users"), CancellationToken())
        print(result)
    else:
        print("❌ 描述表工具未找到")
        return False
    
    # 4. 测试查询
    print("\n4. 测试查询数据 (前5个用户):")
    if query_tool:
        result = await query_tool.run(QueryInput(sql="SELECT * FROM users LIMIT 5"), CancellationToken())
        print(result)
    else:
        print("❌ 查询工具未找到")
        return False
    
    print("\n5. 测试查询统计信息:")
    if query_tool:
        result = await query_tool.run(QueryInput(sql="SELECT COUNT(*) as user_count FROM users"), CancellationToken())
        print(result)
        
        result = await query_tool.run(QueryInput(sql="SELECT COUNT(*) as product_count FROM products"), CancellationToken())
        print(result)
    
    print("\n✅ 所有测试完成!")
    return True

if __name__ == "__main__":
    asyncio.run(test_mysql_tools_detailed())
