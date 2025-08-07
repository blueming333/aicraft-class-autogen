"""
快速飞书连接测试 - 简化版
用于快速测试飞书群组消息发送功能
"""

import os
import requests
import json
from datetime import datetime
from pathlib import Path


def load_env_from_root():
    """从项目根目录加载.env文件"""
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent
    # 获取项目根目录（当前文件在AgentClass目录下）
    root_dir = current_dir.parent
    env_file = root_dir / '.env'
    
    if env_file.exists():
        print(f"📁 正在加载环境变量文件: {env_file}")
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # 移除引号
                        value = value.strip('"').strip("'")
                        os.environ[key] = value
            print("✅ 环境变量加载成功")
            return True
        except Exception as e:
            print(f"⚠️ 加载环境变量失败: {e}")
            return False
    else:
        print(f"⚠️ 未找到环境变量文件: {env_file}")
        print("💡 请确保项目根目录存在 .env 文件")
        return False


def test_feishu_connection():
    """快速测试飞书连接"""
    
    print("🔍 检查飞书配置...")
    
    # 首先尝试从根目录加载.env文件
    load_success = load_env_from_root()
    
    # 获取配置
    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    chat_id = os.getenv('FEISHU_CHAT_ID')
    
    if not all([app_id, app_secret, chat_id]):
        print("❌ 飞书配置不完整")
        print(f"APP_ID: {'✓' if app_id else '✗'}")
        print(f"APP_SECRET: {'✓' if app_secret else '✗'}")  
        print(f"CHAT_ID: {'✓' if chat_id else '✗'}")
        if not load_success:
            print("💡 建议检查项目根目录的 .env 文件")
        return False
    
    print("✓ 配置检查完成")
    
    # 获取访问令牌
    print("\n🔑 获取访问令牌...")
    
    try:
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_data = {
            "app_id": app_id,
            "app_secret": app_secret
        }
        
        response = requests.post(token_url, json=token_data)
        token_result = response.json()
        
        if token_result.get("code") != 0:
            print(f"❌ 获取令牌失败: {token_result}")
            return False
        
        access_token = token_result["tenant_access_token"]
        print("✓ 访问令牌获取成功")
        
    except Exception as e:
        print(f"❌ 获取令牌异常: {e}")
        return False
    
    # 发送测试消息
    print("\n📤 发送测试消息...")
    
    try:
        message_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        test_message = f"🤖 飞书连接测试成功！\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        message_data = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": test_message})
        }
        
        response = requests.post(message_url, json=message_data, headers=headers)
        message_result = response.json()
        
        if message_result.get("code") == 0:
            print("✅ 测试消息发送成功！")
            print(f"消息ID: {message_result.get('data', {}).get('message_id', 'N/A')}")
            return True
        else:
            print(f"❌ 消息发送失败: {message_result}")
            return False
            
    except Exception as e:
        print(f"❌ 消息发送异常: {e}")
        return False


if __name__ == "__main__":
    print("🚀 飞书连接快速测试")
    print("=" * 30)
    
    success = test_feishu_connection()
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 飞书连接测试成功！")
        print("✅ 可以运行完整的Demo7测试程序")
    else:
        print("💥 飞书连接测试失败")
        print("❌ 请检查配置后重试")
    
    print("\n💡 提示:")
    print("- 确保已设置环境变量 FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID")
    print("- 确保机器人已加入目标群聊") 
    print("- 确保应用有发送消息的权限")
