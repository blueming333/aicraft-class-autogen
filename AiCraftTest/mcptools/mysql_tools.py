"""
MySQL工具模块 - 提供MySQL数据库访问工具
参考 AutoGen 的 Tools 接口标准实现
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Type
import json

from pydantic import BaseModel, Field
from autogen_core import CancellationToken, Component
from autogen_core.tools import BaseTool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MySQL数据库配置
MYSQL_CONFIG = {
    "host": "rm-wz98mhtjl6c0x072rbo.mysql.rds.aliyuncs.com",
    "port": 3306,
    "user": "mincode_test", 
    "password": "mincode2025_",
    "database": "mincode_test",
    "charset": "utf8mb4"
}

# 尝试导入MySQL客户端
try:
    import pymysql
    import pymysql.cursors
    MYSQL_AVAILABLE = True
except ImportError:
    try:
        import mysql.connector
        MYSQL_AVAILABLE = True
    except ImportError:
        MYSQL_AVAILABLE = False
        logger.warning("MySQL客户端库未安装 (pymysql 或 mysql-connector-python)")

# ===== 数据模型 =====
class QueryInput(BaseModel):
    """SQL查询输入模型"""
    sql: str = Field(description="SELECT查询语句")
    params: Optional[List] = Field(None, description="查询参数")

class ExecuteInput(BaseModel):
    """SQL执行输入模型"""
    sql: str = Field(description="INSERT/UPDATE/DELETE语句")
    params: Optional[List] = Field(None, description="查询参数")

class TablesInput(BaseModel):
    """获取表列表输入模型"""
    pass

class TableSchemaInput(BaseModel):
    """获取表结构输入模型"""
    table: str = Field(description="表名")

# ===== 工具配置 =====
class MySQLToolConfig(BaseModel):
    name: str
    """工具名称"""
    description: Optional[str]
    """工具描述"""

class MySQLTool(BaseTool[BaseModel, str], Component[MySQLToolConfig]):
    """MySQL工具基类，参考AutoGen工具实现"""
    
    component_type = "tool"
    component_provider_override = "mysql_tools.MySQLTool"
    component_config_schema = MySQLToolConfig
    
    def __init__(
        self,
        name: str,
        input_model: Type[BaseModel],
        description: str = "MySQL工具"
    ) -> None:
        self.tool_params = MySQLToolConfig(
            name=name,
            description=description
        )
        
        # base_return_type始终为str
        base_return_type: Type[str] = str
        
        super().__init__(input_model, base_return_type, name, description)
    
    def _to_config(self) -> MySQLToolConfig:
        return self.tool_params.model_copy()
    
    @classmethod
    def _from_config(cls, config: MySQLToolConfig):
        copied_config = config.model_copy().model_dump()
        return cls(**copied_config)

# 全局连接变量
_mysql_connection = None

def get_mysql_connection():
    """获取MySQL连接"""
    global _mysql_connection
    
    if not MYSQL_AVAILABLE:
        raise Exception("MySQL客户端库未安装")
    
    if _mysql_connection is None or not _mysql_connection.open:
        try:
            _mysql_connection = pymysql.connect(
                host=MYSQL_CONFIG['host'],
                port=MYSQL_CONFIG['port'],
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password'],
                database=MYSQL_CONFIG['database'],
                charset=MYSQL_CONFIG['charset'],
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("MySQL连接已建立")
        except Exception as e:
            logger.error(f"MySQL连接失败: {e}")
            raise e
    
    return _mysql_connection

def initialize_mysql_connection():
    """初始化MySQL连接并保持打开状态"""
    try:
        connection = get_mysql_connection()
        # 测试连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        logger.info(f"MySQL连接初始化成功，测试结果: {result}")
        return True
    except Exception as e:
        logger.error(f"MySQL连接初始化失败: {e}")
        return False

def close_mysql_connection():
    """关闭MySQL连接"""
    global _mysql_connection
    if _mysql_connection:
        _mysql_connection.close()
        _mysql_connection = None
        logger.info("MySQL连接已关闭")

# ===== 工具实现 =====
class QueryTool(MySQLTool):
    """SQL查询工具"""
    
    async def run(self, args: QueryInput, cancellation_token: CancellationToken) -> str:
        """执行SELECT查询"""
        if not args.sql.strip().upper().startswith("SELECT"):
            return "错误: 此工具只允许执行SELECT查询语句"
        
        try:
            connection = get_mysql_connection()
            
            with connection.cursor() as cursor:
                if args.params:
                    cursor.execute(args.sql, args.params)
                else:
                    cursor.execute(args.sql)
                
                results = cursor.fetchall()
                
                if not results:
                    return "查询完成，返回0行记录"
                
                # 格式化结果
                result_text = f"## 查询结果 (共{len(results)}行)\n\n"
                
                # 如果结果较少，显示为表格
                if len(results) <= 10:
                    if results:
                        # 获取列名
                        columns = list(results[0].keys())
                        
                        # 创建表格标题
                        result_text += "| " + " | ".join(columns) + " |\n"
                        result_text += "| " + " | ".join(["---"] * len(columns)) + " |\n"
                        
                        # 添加数据行
                        for row in results:
                            values = [str(row[col]) if row[col] is not None else "NULL" for col in columns]
                            result_text += "| " + " | ".join(values) + " |\n"
                else:
                    # 结果较多时，显示为JSON
                    result_text += "```json\n"
                    result_text += json.dumps(results, ensure_ascii=False, indent=2, default=str)
                    result_text += "\n```"
                
                return result_text
                
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            return f"查询执行失败: {str(e)}"

class ExecuteTool(MySQLTool):
    """SQL执行工具"""
    
    async def run(self, args: ExecuteInput, cancellation_token: CancellationToken) -> str:
        """执行INSERT/UPDATE/DELETE语句"""
        # 检查SQL类型
        sql_upper = args.sql.strip().upper()
        if not (sql_upper.startswith("INSERT") or sql_upper.startswith("UPDATE") or sql_upper.startswith("DELETE")):
            return "错误: 此工具只允许执行INSERT、UPDATE、DELETE语句"
        
        try:
            connection = get_mysql_connection()
            
            with connection.cursor() as cursor:
                if args.params:
                    cursor.execute(args.sql, args.params)
                else:
                    cursor.execute(args.sql)
                
                affected_rows = cursor.rowcount
                connection.commit()
                
                return f"""
## SQL执行成功

- 执行语句: {args.sql[:100]}{"..." if len(args.sql) > 100 else ""}
- 影响行数: {affected_rows}
- 状态: 已提交
"""
                
        except Exception as e:
            logger.error(f"SQL执行失败: {e}")
            connection.rollback()
            return f"SQL执行失败: {str(e)}"

class ListTablesTool(MySQLTool):
    """列举数据库表工具"""
    
    async def run(self, args: TablesInput, cancellation_token: CancellationToken) -> str:
        """列举数据库中的所有表"""
        try:
            connection = get_mysql_connection()
            
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if not tables:
                    return "数据库中没有找到任何表"
                
                # 获取表名（不同MySQL版本返回的键名可能不同）
                table_names = []
                for table in tables:
                    # 获取第一个值（表名）
                    table_name = list(table.values())[0]
                    table_names.append(table_name)
                
                result_text = f"## 数据库表列表 (共{len(table_names)}个表)\n\n"
                
                for i, table_name in enumerate(table_names, 1):
                    result_text += f"{i}. {table_name}\n"
                
                return result_text
                
        except Exception as e:
            logger.error(f"获取表列表失败: {e}")
            return f"获取表列表失败: {str(e)}"

class DescribeTableTool(MySQLTool):
    """查看表结构工具"""
    
    async def run(self, args: TableSchemaInput, cancellation_token: CancellationToken) -> str:
        """查看指定表的结构信息"""
        try:
            connection = get_mysql_connection()
            
            with connection.cursor() as cursor:
                # 使用DESCRIBE或SHOW COLUMNS查看表结构
                cursor.execute(f"DESCRIBE {args.table}")
                columns = cursor.fetchall()
                
                if not columns:
                    return f"表 {args.table} 不存在或没有列信息"
                
                result_text = f"## 表 {args.table} 结构信息\n\n"
                result_text += "| 字段名 | 数据类型 | 允许空值 | 键 | 默认值 | 扩展信息 |\n"
                result_text += "| --- | --- | --- | --- | --- | --- |\n"
                
                for column in columns:
                    field = column.get('Field', '')
                    type_info = column.get('Type', '')
                    null = column.get('Null', '')
                    key = column.get('Key', '')
                    default = column.get('Default', '')
                    extra = column.get('Extra', '')
                    
                    # 处理空值显示
                    default = default if default is not None else "NULL"
                    
                    result_text += f"| {field} | {type_info} | {null} | {key} | {default} | {extra} |\n"
                
                # 获取表的统计信息
                cursor.execute(f"SELECT COUNT(*) as row_count FROM {args.table}")
                count_result = cursor.fetchone()
                row_count = count_result['row_count'] if count_result else 0
                
                result_text += f"\n**表统计信息:**\n- 总行数: {row_count}\n"
                
                return result_text
                
        except Exception as e:
            logger.error(f"获取表结构失败: {e}")
            return f"获取表结构失败: {str(e)}"

# ===== 工具创建函数 =====
def create_mysql_tools():
    """创建所有MySQL工具"""
    # 首先初始化数据库连接
    if not initialize_mysql_connection():
        logger.error("MySQL连接初始化失败，无法创建工具")
        return []
    
    return [
        QueryTool(
            name="query",
            input_model=QueryInput,
            description="执行SELECT查询语句"
        ),
        ExecuteTool(
            name="execute",
            input_model=ExecuteInput,
            description="执行INSERT/UPDATE/DELETE语句"
        ),
        ListTablesTool(
            name="list_tables",
            input_model=TablesInput,
            description="列举数据库中的所有表"
        ),
        DescribeTableTool(
            name="describe_table",
            input_model=TableSchemaInput,
            description="查看指定表的结构信息"
        )
    ]

# ===== 测试函数 =====
async def test_mysql_tools():
    """测试MySQL工具"""
    if not MYSQL_AVAILABLE:
        print("❌ MySQL客户端库未安装")
        return False
    
    print("=== 测试MySQL工具 ===\n")
    
    try:
        # 1. 创建工具（会自动初始化连接）
        tools = create_mysql_tools()
        print(f"✅ 成功创建 {len(tools)} 个MySQL工具:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        if not tools:
            print("❌ 工具创建失败")
            return False
        
        # 2. 测试列表表
        print("\n2. 测试获取表列表:")
        list_tables_tool = None
        for tool in tools:
            if tool.name == "list_tables":
                list_tables_tool = tool
                break
        
        if list_tables_tool:
            from autogen_core import CancellationToken
            result = await list_tables_tool.run(TablesInput(), CancellationToken())
            print(result)
        else:
            print("❌ 列表表工具未找到")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理连接
        close_mysql_connection()

if __name__ == "__main__":
    import asyncio
    
    # 运行测试
    asyncio.run(test_mysql_tools())
