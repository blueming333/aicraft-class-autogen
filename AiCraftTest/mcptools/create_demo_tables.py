#!/usr/bin/env python3
"""
MySQL MCP演示 - 创建表并插入测试数据
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from AiCraftTest.mcptools.mysql_tools import create_mysql_tools, test_mysql_connection

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MySQLDemoManager:
    """MySQL演示管理器"""
    
    def __init__(self):
        self.tools = None
        self.connected = False
        
    async def initialize(self):
        """初始化连接和工具"""
        logger.info("🚀 初始化MySQL MCP连接...")
        
        # 测试连接
        logger.info("🔗 测试连接...")
        self.connected = await test_mysql_connection()
        
        if not self.connected:
            logger.error("❌ 连接失败，无法继续演示")
            return False
            
        logger.info("✅ 连接测试成功!")
        
        # 加载工具
        logger.info("🛠️ 加载MySQL工具...")
        self.tools = await create_mysql_tools()
        
        if not self.tools:
            logger.error("❌ 工具加载失败")
            return False
            
        logger.info(f"✅ 成功加载 {len(self.tools)} 个工具")
        return True
    
    async def create_demo_database(self):
        """创建演示数据库"""
        logger.info("📋 准备创建演示表和数据...")
        
        # 注意：由于MCP工具需要活跃的会话来执行，这里我们展示SQL命令
        # 在实际的MCP环境中，你需要有活跃的会话来执行这些命令
        
        demo_sql_commands = [
            {
                "description": "创建演示数据库",
                "sql": "CREATE DATABASE IF NOT EXISTS demo_aicraft DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            },
            {
                "description": "使用演示数据库",
                "sql": "USE demo_aicraft;"
            },
            {
                "description": "创建用户表",
                "sql": """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    full_name VARCHAR(100) NOT NULL,
                    age INT,
                    city VARCHAR(50),
                    status ENUM('active', 'inactive', 'pending') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_username (username),
                    INDEX idx_email (email),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
            },
            {
                "description": "创建产品表",
                "sql": """
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    stock_quantity INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_category (category),
                    INDEX idx_price (price),
                    INDEX idx_active (is_active)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
            },
            {
                "description": "创建订单表",
                "sql": """
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL DEFAULT 1,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    order_status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_product_id (product_id),
                    INDEX idx_status (order_status),
                    INDEX idx_date (order_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
            }
        ]
        
        return demo_sql_commands
    
    async def create_demo_data(self):
        """创建演示数据"""
        logger.info("📊 准备插入演示数据...")
        
        demo_data_commands = [
            {
                "description": "插入用户数据",
                "sql": """
                INSERT INTO users (username, email, full_name, age, city, status) VALUES
                ('alice_wang', 'alice.wang@example.com', '王爱丽', 28, '北京', 'active'),
                ('bob_zhang', 'bob.zhang@example.com', '张博', 32, '上海', 'active'),
                ('carol_li', 'carol.li@example.com', '李卡罗', 25, '深圳', 'active'),
                ('david_chen', 'david.chen@example.com', '陈大卫', 35, '广州', 'inactive'),
                ('eva_liu', 'eva.liu@example.com', '刘伊娃', 29, '杭州', 'active'),
                ('frank_wu', 'frank.wu@example.com', '吴法兰', 27, '成都', 'pending'),
                ('grace_huang', 'grace.huang@example.com', '黄格蕾丝', 31, '武汉', 'active'),
                ('henry_zhao', 'henry.zhao@example.com', '赵亨利', 26, '西安', 'active'),
                ('iris_tang', 'iris.tang@example.com', '唐艾瑞丝', 30, '南京', 'active'),
                ('jack_feng', 'jack.feng@example.com', '冯杰克', 33, '重庆', 'inactive');
                """
            },
            {
                "description": "插入产品数据",
                "sql": """
                INSERT INTO products (name, description, price, category, stock_quantity, is_active) VALUES
                ('MacBook Pro 14寸', '苹果笔记本电脑，M3芯片，16GB内存，512GB存储', 15999.00, '电脑', 50, TRUE),
                ('iPhone 15 Pro', '苹果智能手机，A17 Pro芯片，256GB存储', 8999.00, '手机', 100, TRUE),
                ('iPad Air', '苹果平板电脑，M2芯片，256GB Wi-Fi版', 4999.00, '平板', 75, TRUE),
                ('AirPods Pro 2', '苹果无线耳机，主动降噪', 1899.00, '音频', 200, TRUE),
                ('Magic Keyboard', '苹果无线键盘，中文版', 799.00, '配件', 150, TRUE),
                ('Magic Mouse', '苹果无线鼠标，白色', 629.00, '配件', 120, TRUE),
                ('Apple Watch Series 9', '苹果智能手表，45mm GPS版', 3199.00, '穿戴', 80, TRUE),
                ('Studio Display', '苹果27寸5K显示器', 11499.00, '显示器', 30, TRUE),
                ('Mac mini', '苹果桌面电脑，M2芯片，8GB+256GB', 4499.00, '电脑', 60, TRUE),
                ('HomePod mini', '苹果智能音箱，深空灰', 749.00, '音频', 90, FALSE);
                """
            },
            {
                "description": "插入订单数据",
                "sql": """
                INSERT INTO orders (user_id, product_id, quantity, unit_price, total_amount, order_status, order_date) VALUES
                (1, 1, 1, 15999.00, 15999.00, 'delivered', '2024-07-15 10:30:00'),
                (1, 4, 1, 1899.00, 1899.00, 'delivered', '2024-07-15 10:35:00'),
                (2, 2, 1, 8999.00, 8999.00, 'shipped', '2024-07-20 14:20:00'),
                (3, 3, 1, 4999.00, 4999.00, 'confirmed', '2024-07-25 16:45:00'),
                (3, 5, 1, 799.00, 799.00, 'confirmed', '2024-07-25 16:50:00'),
                (5, 7, 1, 3199.00, 3199.00, 'pending', '2024-08-01 09:15:00'),
                (7, 9, 1, 4499.00, 4499.00, 'delivered', '2024-08-03 11:30:00'),
                (8, 6, 2, 629.00, 1258.00, 'shipped', '2024-08-05 15:20:00'),
                (9, 8, 1, 11499.00, 11499.00, 'pending', '2024-08-06 13:45:00'),
                (1, 10, 1, 749.00, 749.00, 'cancelled', '2024-08-07 08:30:00');
                """
            }
        ]
        
        return demo_data_commands
    
    async def create_demo_queries(self):
        """创建演示查询"""
        logger.info("🔍 准备演示查询...")
        
        demo_queries = [
            {
                "description": "查看所有用户",
                "sql": "SELECT id, username, full_name, city, status, created_at FROM users ORDER BY created_at;"
            },
            {
                "description": "查看活跃用户数量",
                "sql": "SELECT status, COUNT(*) as user_count FROM users GROUP BY status;"
            },
            {
                "description": "查看所有产品",
                "sql": "SELECT id, name, price, category, stock_quantity, is_active FROM products ORDER BY category, price;"
            },
            {
                "description": "查看不同类别产品数量",
                "sql": "SELECT category, COUNT(*) as product_count, AVG(price) as avg_price FROM products WHERE is_active = TRUE GROUP BY category;"
            },
            {
                "description": "查看所有订单",
                "sql": "SELECT o.id, u.full_name, p.name, o.quantity, o.total_amount, o.order_status, o.order_date FROM orders o JOIN users u ON o.user_id = u.id JOIN products p ON o.product_id = p.id ORDER BY o.order_date DESC;"
            },
            {
                "description": "查看订单统计",
                "sql": "SELECT order_status, COUNT(*) as order_count, SUM(total_amount) as total_revenue FROM orders GROUP BY order_status;"
            },
            {
                "description": "查看用户购买统计",
                "sql": "SELECT u.full_name, COUNT(o.id) as order_count, SUM(o.total_amount) as total_spent FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.full_name ORDER BY total_spent DESC;"
            },
            {
                "description": "查看热门产品",
                "sql": "SELECT p.name, COUNT(o.id) as order_count, SUM(o.quantity) as total_sold, SUM(o.total_amount) as total_revenue FROM products p LEFT JOIN orders o ON p.id = o.product_id WHERE o.order_status != 'cancelled' GROUP BY p.id, p.name ORDER BY total_sold DESC LIMIT 5;"
            }
        ]
        
        return demo_queries
    
    async def run_demo(self):
        """运行完整演示"""
        print("\n" + "="*60)
        print("🗄️  MySQL MCP 演示系统")
        print("="*60)
        
        # 初始化
        if not await self.initialize():
            print("❌ 初始化失败，演示终止")
            return
            
        print(f"\n📋 可用的MySQL工具:")
        for i, tool in enumerate(self.tools, 1):
            print(f"   {i}. {tool.name}")
        
        # 生成SQL命令
        print(f"\n📝 生成演示SQL命令...")
        
        # 创建表的命令
        table_commands = await self.create_demo_database()
        print(f"\n🏗️  数据库结构创建命令 ({len(table_commands)} 个):")
        for i, cmd in enumerate(table_commands, 1):
            print(f"\n--- {i}. {cmd['description']} ---")
            print(cmd['sql'].strip())
        
        # 插入数据的命令
        data_commands = await self.create_demo_data()
        print(f"\n📊 测试数据插入命令 ({len(data_commands)} 个):")
        for i, cmd in enumerate(data_commands, 1):
            print(f"\n--- {i}. {cmd['description']} ---")
            print(cmd['sql'].strip())
        
        # 演示查询
        query_commands = await self.create_demo_queries()
        print(f"\n🔍 演示查询命令 ({len(query_commands)} 个):")
        for i, cmd in enumerate(query_commands, 1):
            print(f"\n--- {i}. {cmd['description']} ---")
            print(cmd['sql'].strip())
        
        print(f"\n" + "="*60)
        print("📄 完整SQL脚本已生成")
        print("="*60)
        
        # 保存到文件
        await self.save_sql_scripts(table_commands, data_commands, query_commands)
        
        print("\n💡 如何使用这些SQL命令:")
        print("   1. 复制SQL命令到MySQL客户端执行")
        print("   2. 或者在Web界面中使用 'execute' 工具执行")
        print("   3. 使用 'query' 工具执行SELECT查询")
        print("   4. 使用 'list_tables' 查看创建的表")
        print("   5. 使用 'describe_table' 查看表结构")
        
    async def save_sql_scripts(self, table_commands, data_commands, query_commands):
        """保存SQL脚本到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存完整的SQL脚本
        full_script_path = f"mysql_demo_full_{timestamp}.sql"
        with open(full_script_path, 'w', encoding='utf-8') as f:
            f.write("-- MySQL MCP 演示数据库脚本\n")
            f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("-- ==============================================\n")
            f.write("-- 1. 数据库和表结构创建\n")
            f.write("-- ==============================================\n\n")
            for cmd in table_commands:
                f.write(f"-- {cmd['description']}\n")
                f.write(cmd['sql'].strip() + "\n\n")
            
            f.write("-- ==============================================\n")
            f.write("-- 2. 测试数据插入\n")
            f.write("-- ==============================================\n\n")
            for cmd in data_commands:
                f.write(f"-- {cmd['description']}\n")
                f.write(cmd['sql'].strip() + "\n\n")
            
            f.write("-- ==============================================\n")
            f.write("-- 3. 演示查询\n")
            f.write("-- ==============================================\n\n")
            for cmd in query_commands:
                f.write(f"-- {cmd['description']}\n")
                f.write(f"-- {cmd['sql'].strip()}\n\n")
        
        # 保存Web演示用的JSON配置
        web_config = {
            "timestamp": timestamp,
            "description": "MySQL MCP演示配置",
            "database_setup": table_commands,
            "test_data": data_commands,
            "demo_queries": query_commands,
            "usage_instructions": [
                "使用 connect_db 工具连接到MySQL服务器",
                "使用 execute 工具执行DDL和DML语句",
                "使用 query 工具执行SELECT查询",
                "使用 list_tables 查看所有表",
                "使用 describe_table 查看表结构"
            ]
        }
        
        config_path = f"mysql_demo_config_{timestamp}.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(web_config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ SQL脚本已保存到: {full_script_path}")
        print(f"✅ 配置文件已保存到: {config_path}")

async def main():
    """主函数"""
    demo = MySQLDemoManager()
    await demo.run_demo()

if __name__ == "__main__":
    print("🚀 启动MySQL MCP演示...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 演示已中止")
    except Exception as e:
        print(f"❌ 演示异常: {e}")
        import traceback
        traceback.print_exc()
