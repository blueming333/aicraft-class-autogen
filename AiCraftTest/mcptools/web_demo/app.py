#!/usr/bin/env python3
"""
MySQL MCP 交互式演示 - Flask Web应用 (集成AutoGen Agent)
"""

import asyncio
import json
import logging
import sys
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 添加项目根目录到路径
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../../..')
sys.path.append(project_root)

# 加载环境变量
load_dotenv(os.path.join(project_root, '.env'))

# 导入AutoGen相关组件
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_agentchat.ui import Console

from AiCraftTest.mcptools.mysql_tools import create_mysql_tools, test_mysql_tools

# 配置日志
logging.basicConfig(level=logging.INFO)  # 改为INFO级别，减少调试输出
logger = logging.getLogger(__name__)

# 设置特定模块的日志级别，减少调试噪音
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING) 
logging.getLogger('mcp.client.streamable_http').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('autogen_core.events').setLevel(logging.WARNING)
logging.getLogger('autogen_agentchat.events').setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量存储MySQL工具和Agent
mysql_tools = None
mysql_session = None
database_agent = None

# 配置模型客户端
def create_model_client():
    """创建模型客户端"""
    # 设置OpenAI API配置
    os.environ.setdefault("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("未找到OPENAI_API_KEY环境变量")
        return None
    
    try:
        model_client = OpenAIChatCompletionClient(
            model="qwen-plus",  # 使用阿里千问，支持函数调用
            model_info={
                "function_calling": True,
                "json_output": True,
                "vision": False,
                "stream": False,
                "structured_output": True,
                "family": ModelFamily.UNKNOWN,
            },
            max_tokens=4096,
        )
        return model_client
    except Exception as e:
        logger.error(f"创建模型客户端失败: {e}")
        return None

def initialize_database_agent():
    """初始化数据库Agent（同步版本）"""
    global database_agent, mysql_tools
    
    try:
        # 创建模型客户端
        model_client = create_model_client()
        if not model_client:
            logger.error("模型客户端创建失败")
            return False
        
        # 加载MySQL工具 - 使用本地MySQL工具方式获取正确的AutoGen工具
        mysql_tools = create_mysql_tools()
        
        if not mysql_tools:
            logger.error("MySQL工具加载失败")
            return False
        
        logger.info(f"成功加载 {len(mysql_tools)} 个MySQL工具")
        
        # 创建数据库分析师Agent
        database_agent = AssistantAgent(
            name="DatabaseAnalyst",
            tools=mysql_tools,
            model_client=model_client,
            system_message="""你是一个专业的MySQL数据库分析师，帮助用户查询和分析数据。

## 可用工具
- query: 执行SELECT查询  
- execute: 执行INSERT/UPDATE/DELETE操作
- list_tables: 查看所有表
- describe_table: 查看表结构

## 数据库信息
数据库连接已自动建立，无需手动连接：
- 服务器: rm-wz98mhtjl6c0x072rbo.mysql.rds.aliyuncs.com:3306
- 数据库: mincode_test

## 主要数据表
- users: 用户信息(id, username, email, full_name, age, city, status)
- products: 产品信息(id, name, description, price, category, stock_quantity)
- orders: 订单记录(id, user_id, product_id, quantity, unit_price, total_amount)

## 工作流程
1. 使用list_tables查看所有表
2. 使用describe_table了解表结构
3. 构建SQL查询并执行
4. 用清晰格式展示数据

数据库连接已预先建立，直接开始查询分析即可。""",
            model_client_stream=False
        )
        
        logger.info("数据库Agent初始化成功")
        return True
        
    except Exception as e:
        logger.error(f"初始化数据库Agent失败: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/initialize-agent', methods=['POST'])
def initialize_agent():
    """初始化数据库Agent"""
    try:
        logger.info("开始初始化数据库Agent...")
        
        # 直接调用同步版本的初始化函数
        success = initialize_database_agent()
        
        if success:
            return jsonify({
                'success': True,
                'message': '✅ 数据库Agent初始化成功！现在可以使用自然语言查询数据了',
                'agent_name': 'DatabaseAnalyst',
                'tools_count': len(mysql_tools) if mysql_tools else 0,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ 数据库Agent初始化失败',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"初始化Agent异常: {e}")
        return jsonify({
            'success': False,
            'message': f'初始化Agent异常: {str(e)}',
            'error': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/natural-query', methods=['POST'])
def natural_query():
    """处理自然语言数据库查询"""
    global database_agent
    
    try:
        if not database_agent:
            return jsonify({
                'success': False,
                'message': '❌ 请先初始化数据库Agent',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        data = request.get_json()
        user_query = data.get('query')
        
        if not user_query:
            return jsonify({
                'success': False,
                'message': '❌ 缺少查询内容',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        logger.info(f"处理自然语言查询: {user_query}")
        
        # 使用Agent处理查询
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 创建一个简单的运行环境来执行Agent
        response = loop.run_until_complete(run_agent_query(user_query))
        loop.close()
        
        return jsonify({
            'success': True,
            'query': user_query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"自然语言查询异常: {e}")
        return jsonify({
            'success': False,
            'message': f'查询处理异常: {str(e)}',
            'error': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }), 500

async def run_agent_query(user_query):
    """运行真实的Agent查询"""
    global database_agent
    
    try:
        logger.info(f"开始执行Agent查询: {user_query}")
        
        # 使用agent.run()方法执行任务
        result = await database_agent.run(task=user_query)
        print(result.messages[-1].content)
        
        # 提取响应内容
        if result and hasattr(result, 'messages') and result.messages:
            # 获取最后一条消息的内容
            last_message = result.messages[-1]
            if hasattr(last_message, 'content'):
                response = last_message.content
            else:
                response = str(last_message)
        elif result:
            response = str(result)
        else:
            response = "Agent执行完成，但未返回具体结果"
        
        logger.info("Agent查询执行完成")
        return response
            
    except Exception as e:
        logger.error(f"Agent查询执行异常: {e}")
        import traceback
        traceback.print_exc()
        return f"查询处理失败: {str(e)}\n\n请确保已正确配置数据库连接信息并初始化Agent。"
@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """测试MySQL MCP连接"""
    try:
        logger.info("开始测试MySQL MCP连接...")
        
        # 使用asyncio运行异步测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(test_mysql_tools())
        loop.close()
        
        if success:
            return jsonify({
                'success': True,
                'message': '✅ MySQL MCP连接测试成功！',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ MySQL MCP连接测试失败！',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"连接测试异常: {e}")
        return jsonify({
            'success': False,
            'message': f'连接测试异常: {str(e)}',
            'error': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/load-tools', methods=['POST'])
def load_tools():
    """加载MySQL工具"""
    global mysql_tools
    
    try:
        logger.info("开始加载MySQL工具...")
        
        # 使用asyncio运行异步操作
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 使用简化工具方式加载工具
        async def load_mysql_tools_async():
            return create_mysql_tools()
        
        mysql_tools = loop.run_until_complete(load_mysql_tools_async())
        loop.close()
        
        if mysql_tools:
            tools_info = []
            for tool in mysql_tools:
                tool_info = {
                    'name': tool.__name__ if hasattr(tool, '__name__') else str(tool),
                    'description': getattr(tool, '__doc__', '无描述') or '无描述'
                }
                tools_info.append(tool_info)
            
            return jsonify({
                'success': True,
                'message': f'✅ 成功加载 {len(mysql_tools)} 个MySQL工具',
                'tools': tools_info,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ 未能加载MySQL工具',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"加载工具异常: {e}")
        return jsonify({
            'success': False,
            'message': f'加载工具异常: {str(e)}',
            'error': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/execute-tool', methods=['POST'])
def execute_tool():
    """执行MySQL工具"""
    global mysql_tools
    
    try:
        if not mysql_tools:
            return jsonify({
                'success': False,
                'message': '❌ 请先加载MySQL工具',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        data = request.get_json()
        tool_name = data.get('tool_name')
        tool_args = data.get('args', {})
        
        if not tool_name:
            return jsonify({
                'success': False,
                'message': '❌ 缺少工具名称',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 查找对应的工具
        target_tool = None
        for tool in mysql_tools:
            if tool.name == tool_name:
                target_tool = tool
                break
        
        if not target_tool:
            return jsonify({
                'success': False,
                'message': f'❌ 未找到工具: {tool_name}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        logger.info(f"执行工具: {tool_name}, 参数: {tool_args}")
        
        # 注意：这里简化处理，实际的工具执行需要更复杂的MCP会话管理
        # 由于工具执行需要活跃的MCP会话，这里返回模拟结果
        return jsonify({
            'success': True,
            'message': f'✅ 工具 {tool_name} 执行请求已发送',
            'tool_name': tool_name,
            'args': tool_args,
            'note': '注意：实际工具执行需要活跃的MCP会话，这里显示的是模拟结果',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"工具执行异常: {e}")
        return jsonify({
            'success': False,
            'message': f'工具执行异常: {str(e)}',
            'error': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/get-tool-info/<tool_name>', methods=['GET'])
def get_tool_info(tool_name):
    """获取特定工具的详细信息"""
    global mysql_tools
    
    try:
        if not mysql_tools:
            return jsonify({
                'success': False,
                'message': '❌ 请先加载MySQL工具',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 查找工具
        for tool in mysql_tools:
            if tool.name == tool_name:
                tool_info = {
                    'name': tool.name,
                    'description': getattr(tool, 'description', '无描述'),
                    'timestamp': datetime.now().isoformat()
                }
                
                # 添加输入模式信息
                if hasattr(tool, 'inputSchema'):
                    try:
                        tool_info['inputSchema'] = tool.inputSchema
                    except:
                        tool_info['inputSchema'] = str(tool.inputSchema)
                
                return jsonify({
                    'success': True,
                    'tool': tool_info
                })
        
        return jsonify({
            'success': False,
            'message': f'❌ 未找到工具: {tool_name}',
            'timestamp': datetime.now().isoformat()
        }), 404
        
    except Exception as e:
        logger.error(f"获取工具信息异常: {e}")
        return jsonify({
            'success': False,
            'message': f'获取工具信息异常: {str(e)}',
            'error': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    global mysql_tools
    
    return jsonify({
        'success': True,
        'status': {
            'tools_loaded': mysql_tools is not None,
            'tools_count': len(mysql_tools) if mysql_tools else 0,
            'timestamp': datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    print("🚀 启动MySQL MCP交互式演示...")
    print("📱 访问地址: http://localhost:5001")
    print("🔧 API端点:")
    print("   - POST /api/test-connection - 测试连接")
    print("   - POST /api/load-tools - 加载工具")
    print("   - POST /api/execute-tool - 执行工具")
    print("   - GET  /api/get-tool-info/<tool_name> - 获取工具信息")
    print("   - GET  /api/status - 获取状态")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
