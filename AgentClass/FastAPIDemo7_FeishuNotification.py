"""
AgentClass Demo7 - 飞书群组通知测试
演示如何使用通知系统向飞书群组发送各种类型的消息
"""

import os
import logging
import asyncio
import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_env_from_root():
    """从项目根目录加载.env文件"""
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent
    # 获取项目根目录（当前文件在AgentClass目录下）
    root_dir = current_dir.parent
    env_file = root_dir / '.env'
    
    if env_file.exists():
        logger.info(f"正在加载环境变量文件: {env_file}")
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # 移除引号
                        value = value.strip('"').strip("'")
                        os.environ[key] = value
            logger.info("✅ 环境变量加载成功")
        except Exception as e:
            logger.warning(f"⚠️ 加载环境变量失败: {e}")
    else:
        logger.warning(f"⚠️ 未找到环境变量文件: {env_file}")

# 在模块导入时自动加载环境变量
load_env_from_root()


class FeishuAPI:
    """飞书API客户端"""
    
    def __init__(self, app_id: str, app_secret: str, chat_id: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.chat_id = chat_id
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
    
    def get_access_token(self) -> str:
        """获取飞书访问token"""
        try:
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            headers = {"Content-Type": "application/json"}
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result["tenant_access_token"]
                logger.info("飞书访问token获取成功")
                return self.access_token
            else:
                logger.error(f"飞书token获取失败: {result}")
                return None
                
        except Exception as e:
            logger.error(f"飞书token获取异常: {str(e)}")
            return None
    
    def send_text_message(self, text: str) -> Dict[str, Any]:
        """发送文本消息"""
        if not self.access_token:
            if not self.get_access_token():
                return {"success": False, "error": "无法获取访问token"}
        
        try:
            url = f"{self.base_url}/im/v1/messages?receive_id_type=chat_id"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 正确构建JSON内容
            content = {
                "text": text
            }
            
            data = {
                "receive_id": self.chat_id,
                "msg_type": "text",
                "content": json.dumps(content)
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"飞书文本消息发送成功")
                return {"success": True, "data": result.get("data")}
            else:
                logger.error(f"飞书文本消息发送失败: {result}")
                return {"success": False, "error": result.get("msg", "未知错误")}
                
        except Exception as e:
            logger.error(f"飞书文本消息发送异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_rich_text_message(self, title: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """发送富文本消息"""
        if not self.access_token:
            if not self.get_access_token():
                return {"success": False, "error": "无法获取访问token"}
        
        try:
            url = f"{self.base_url}/im/v1/messages?receive_id_type=chat_id"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 构建富文本内容
            rich_content = {
                "zh_cn": {
                    "title": title,
                    "content": content.get("content", [])
                }
            }
            
            data = {
                "receive_id": self.chat_id,
                "msg_type": "post",
                "content": json.dumps(rich_content)
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"飞书富文本消息发送成功")
                return {"success": True, "data": result.get("data")}
            else:
                logger.error(f"飞书富文本消息发送失败: {result}")
                return {"success": False, "error": result.get("msg", "未知错误")}
                
        except Exception as e:
            logger.error(f"飞书富文本消息发送异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_warning_message(self, warning_type: str, title: str, details: Dict[str, Any], level: str = "normal") -> Dict[str, Any]:
        """发送预警消息"""
        try:
            # 根据级别设置颜色
            level_colors = {
                "high": "🔴",
                "normal": "🟡", 
                "low": "🟢"
            }
            
            color = level_colors.get(level, "🔵")
            
            # 构建预警消息内容
            warning_text = f"{color} 【{warning_type}】{title}\n\n"
            
            for key, value in details.items():
                warning_text += f"• {key}: {value}\n"
            
            warning_text += f"\n⏰ 发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return self.send_text_message(warning_text)
            
        except Exception as e:
            logger.error(f"发送预警消息异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def is_available(self) -> bool:
        """检查飞书API是否可用"""
        return bool(self.app_id and self.app_secret and self.chat_id)


class FeishuNotificationDemo:
    """飞书通知演示类"""
    
    def __init__(self):
        self.feishu_client = None
        self._init_feishu_client()
    
    def _init_feishu_client(self):
        """初始化飞书客户端"""
        # 从环境变量获取配置
        app_id = os.getenv('FEISHU_APP_ID')
        app_secret = os.getenv('FEISHU_APP_SECRET') 
        chat_id = os.getenv('FEISHU_CHAT_ID')
        
        if not all([app_id, app_secret, chat_id]):
            logger.warning("飞书配置不完整，请设置以下环境变量:")
            logger.warning("- FEISHU_APP_ID")
            logger.warning("- FEISHU_APP_SECRET")
            logger.warning("- FEISHU_CHAT_ID")
            
            # 使用测试配置（如果有的话）
            app_id = app_id or "cli_test_app_id"
            app_secret = app_secret or "test_app_secret"
            chat_id = chat_id or "oc_test_chat_id"
        
        self.feishu_client = FeishuAPI(app_id, app_secret, chat_id)
        logger.info("飞书客户端初始化完成")
    
    def test_simple_text(self) -> Dict[str, Any]:
        """测试简单文本消息"""
        logger.info("=== 测试简单文本消息 ===")
        
        if not self.feishu_client.is_available():
            return {"success": False, "error": "飞书客户端不可用"}
        
        message = f"🤖 AgentClass Demo7 测试消息\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        result = self.feishu_client.send_text_message(message)
        
        if result["success"]:
            logger.info("✅ 简单文本消息发送成功")
        else:
            logger.error(f"❌ 简单文本消息发送失败: {result.get('error')}")
        
        return result
    
    def test_project_warning(self) -> Dict[str, Any]:
        """测试项目预警通知"""
        logger.info("=== 测试项目预警通知 ===")
        
        if not self.feishu_client.is_available():
            return {"success": False, "error": "飞书客户端不可用"}
        
        # 模拟项目预警数据
        warning_data = {
            "项目名称": "AI聊天机器人开发",
            "开发者": "张三",
            "连续无提交天数": "5天",
            "历史提交总数": "12次",
            "预警级别": "高",
            "订单ID": "ORDER-2024-001",
            "预警原因": "项目进度严重滞后，需要及时关注"
        }
        
        result = self.feishu_client.send_warning_message(
            warning_type="项目提交预警",
            title="项目进度预警 - AI聊天机器人开发",
            details=warning_data,
            level="high"
        )
        
        if result["success"]:
            logger.info("✅ 项目预警通知发送成功")
        else:
            logger.error(f"❌ 项目预警通知发送失败: {result.get('error')}")
        
        return result
    
    def test_order_notification(self) -> Dict[str, Any]:
        """测试订单通知"""
        logger.info("=== 测试订单通知 ===")
        
        if not self.feishu_client.is_available():
            return {"success": False, "error": "飞书客户端不可用"}
        
        order_data = {
            "订单类型": "前端开发",
            "报名开发者": "李四",
            "订单预算": "￥5000",
            "项目周期": "2周",
            "技术栈": "Vue.js, Element-UI",
            "客户要求": "响应式设计，兼容移动端"
        }
        
        result = self.feishu_client.send_warning_message(
            warning_type="订单报名通知",
            title="新订单报名 - 前端开发项目",
            details=order_data,
            level="normal"
        )
        
        if result["success"]:
            logger.info("✅ 订单通知发送成功")
        else:
            logger.error(f"❌ 订单通知发送失败: {result.get('error')}")
        
        return result
    
    def test_milestone_notification(self) -> Dict[str, Any]:
        """测试里程碑通知"""
        logger.info("=== 测试里程碑通知 ===")
        
        if not self.feishu_client.is_available():
            return {"success": False, "error": "飞书客户端不可用"}
        
        milestone_data = {
            "项目名称": "电商管理系统",
            "里程碑": "用户管理模块",
            "完成状态": "已提交验收",
            "开发者": "王五",
            "提交时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "里程碑金额": "￥2000",
            "验收要求": "功能测试通过，代码review完成"
        }
        
        result = self.feishu_client.send_warning_message(
            warning_type="里程碑完成通知",
            title="里程碑提交验收 - 用户管理模块",
            details=milestone_data,
            level="high"
        )
        
        if result["success"]:
            logger.info("✅ 里程碑通知发送成功")
        else:
            logger.error(f"❌ 里程碑通知发送失败: {result.get('error')}")
        
        return result
    
    def test_system_notification(self) -> Dict[str, Any]:
        """测试系统通知"""
        logger.info("=== 测试系统通知 ===")
        
        if not self.feishu_client.is_available():
            return {"success": False, "error": "飞书客户端不可用"}
        
        system_data = {
            "系统名称": "AiCraft平台",
            "通知类型": "系统维护",
            "维护时间": "2024-01-15 02:00-04:00",
            "影响范围": "订单提交、支付功能",
            "维护内容": "数据库优化，性能提升",
            "联系方式": "技术支持群"
        }
        
        result = self.feishu_client.send_warning_message(
            warning_type="系统维护通知",
            title="平台维护通知 - 定期系统优化",
            details=system_data,
            level="normal"
        )
        
        if result["success"]:
            logger.info("✅ 系统通知发送成功")
        else:
            logger.error(f"❌ 系统通知发送失败: {result.get('error')}")
        
        return result
    
    def test_batch_notifications(self) -> Dict[str, Any]:
        """测试批量通知"""
        logger.info("=== 测试批量通知 ===")
        
        results = []
        
        # 发送多个不同类型的通知
        notifications = [
            {
                "type": "用户注册通知",
                "title": "新用户注册 - 赵六",
                "details": {
                    "用户名": "赵六",
                    "注册时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "用户类型": "开发者",
                    "技能标签": "Python, Django, Vue.js",
                    "所在城市": "北京"
                },
                "level": "low"
            },
            {
                "type": "支付成功通知", 
                "title": "订单支付完成 - ORDER-2024-002",
                "details": {
                    "订单号": "ORDER-2024-002",
                    "支付金额": "￥3000",
                    "支付方式": "微信支付",
                    "客户": "客户A",
                    "开发者": "开发者B",
                    "项目": "小程序开发"
                },
                "level": "normal"
            },
            {
                "type": "紧急故障通知",
                "title": "系统异常 - 数据库连接超时",
                "details": {
                    "故障类型": "数据库连接超时",
                    "影响范围": "用户登录，订单查询",
                    "发现时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "预计修复时间": "30分钟",
                    "临时解决方案": "已切换备用数据库"
                },
                "level": "high"
            }
        ]
        
        for notification in notifications:
            result = self.feishu_client.send_warning_message(
                warning_type=notification["type"],
                title=notification["title"],
                details=notification["details"],
                level=notification["level"]
            )
            results.append({
                "type": notification["type"],
                "success": result["success"],
                "error": result.get("error")
            })
            
            # 避免频率限制
            time.sleep(0.5)
        
        success_count = sum(1 for r in results if r["success"])
        
        logger.info(f"✅ 批量通知发送完成: 成功 {success_count}/{len(results)} 条")
        
        return {
            "success": success_count > 0,
            "total": len(results),
            "success_count": success_count,
            "results": results
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始飞书通知系统测试")
        logger.info("=" * 50)
        
        tests = [
            ("简单文本消息", self.test_simple_text),
            ("项目预警通知", self.test_project_warning),
            ("订单通知", self.test_order_notification),
            ("里程碑通知", self.test_milestone_notification),
            ("系统通知", self.test_system_notification),
            ("批量通知", self.test_batch_notifications)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                logger.info(f"\n🔄 正在执行: {test_name}")
                result = test_func()
                results[test_name] = result
                
                if result.get("success"):
                    logger.info(f"✅ {test_name} - 执行成功")
                else:
                    logger.error(f"❌ {test_name} - 执行失败: {result.get('error')}")
                
            except Exception as e:
                logger.error(f"❌ {test_name} - 执行异常: {str(e)}")
                results[test_name] = {"success": False, "error": str(e)}
        
        # 统计结果
        success_tests = [name for name, result in results.items() if result.get("success")]
        failed_tests = [name for name, result in results.items() if not result.get("success")]
        
        logger.info("\n" + "=" * 50)
        logger.info("📊 测试结果统计:")
        logger.info(f"✅ 成功: {len(success_tests)} 项")
        logger.info(f"❌ 失败: {len(failed_tests)} 项")
        
        if success_tests:
            logger.info(f"🎉 成功的测试: {', '.join(success_tests)}")
        
        if failed_tests:
            logger.error(f"💥 失败的测试: {', '.join(failed_tests)}")
            
        logger.info("=" * 50)
        logger.info("🏁 飞书通知系统测试完成")
        
        return results


def main():
    """主函数"""
    logger.info("🤖 AgentClass Demo7 - 飞书群组通知测试")
    
    # 检查环境变量
    env_vars = ['FEISHU_APP_ID', 'FEISHU_APP_SECRET', 'FEISHU_CHAT_ID']
    missing_vars = [var for var in env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"⚠️ 缺少环境变量: {', '.join(missing_vars)}")
        logger.warning("请在 .env 文件中设置这些变量，或者直接设置环境变量")
        logger.info("\n示例配置:")
        logger.info("FEISHU_APP_ID=cli_xxxxxxxxxx")
        logger.info("FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx")
        logger.info("FEISHU_CHAT_ID=oc_xxxxxxxxxxxxxxxx")
        logger.info("\n继续运行测试（使用模拟配置）...")
    
    # 创建演示实例
    demo = FeishuNotificationDemo()
    
    # 运行所有测试
    demo.run_all_tests()


if __name__ == "__main__":
    main()
